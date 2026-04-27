import os
import threading
import uuid
from datetime import datetime, timezone
from itertools import cycle
from time import sleep

import yaml
from ollama import Client


class Session:
    WINDOW_SIZE = 30

    def __init__(self, model='gpt-oss:20b', output_path=None, resume_path=None, client=None):
        self.client = client or Client()
        self.model = model
        self.output_path = output_path
        self.system_prompt = (
            'You are a creative writing assistant. Help the user write an interactive story. '
            'Maintain continuity, tone, characters, and plot details from prior context. '
            'Be imaginative but coherent, and when appropriate propose concise next-scene options.'
            "Stay consistent with the supplied world, characters, and plot facts."
            "Do not contradict established facts unless the user explicitly revises them."
            "Preserve character voice and relationship dynamics."
            "Prefer natural scene continuation over exposition dumps."
            "When uncertain, follow the most specific fact in the story bible."
            # Story Bibles would be added here.
        )

        # for now, give it the model name
        self.assistant_name = model

        if resume_path:
            self._load_from_file(resume_path)
            if output_path:
                self.output_path = output_path
            else:
                self.output_path = resume_path
            self.is_resumed = True
        else:
            self.is_resumed = False
            self.session_id = str(uuid.uuid4())
            now = self._now_iso()
            self.created_at = now
            self.updated_at = now
            self.ended_at = None
            self.status = 'active'
            self.messages = []
            self.summaries = []
            self.rolling_summary = ''
            self.summarized_through_message = 0
            if not self.output_path:
                os.makedirs('sessions', exist_ok=True)
                self.output_path = os.path.join('sessions', f'{self.session_id}.yaml')

    def add_user_message(self, content):
        self._append_message('user', content)

    def add_assistant_message(self, content):
        self._append_message('assistant', content)

    def _append_message(self, role, content):
        message = {
            'index': len(self.messages) + 1,
            'role': role,
            'content': content,
            'timestamp': self._now_iso(),
        }
        self.messages.append(message)
        self.updated_at = self._now_iso()
        self._maybe_update_rolling_summary()

    def _unsummarized_messages(self):
        return self.messages[self.summarized_through_message:]

    def _maybe_update_rolling_summary(self):
        unsummarized = self._unsummarized_messages()
        while len(unsummarized) > self.WINDOW_SIZE:
            block = unsummarized[: self.WINDOW_SIZE]
            start_index = block[0]['index']
            end_index = block[-1]['index']
            next_summary = self._summarize_block(block)
            self.rolling_summary = next_summary
            self.summarized_through_message = end_index
            self.summaries.append(
                {
                    'index': len(self.summaries) + 1,
                    'covers_messages': [1, end_index],
                    'content': next_summary,
                    'timestamp': self._now_iso(),
                }
            )
            unsummarized = self._unsummarized_messages()

    def _summarize_block(self, block):
        lines = []
        for msg in block:
            lines.append(f"{msg['role'].upper()}[{msg['index']}]: {msg['content']}")

        summary_messages = [
            {
                'role': 'system',
                'content': (
                    'Summarize story-writing conversation context for future continuation. '
                    'Keep critical plot details, character motivations, unresolved threads, style choices, '
                    'and user preferences. Keep it concise but complete.'
                ),
            }
        ]

        if self.rolling_summary:
            summary_messages.append(
                {
                    'role': 'system',
                    'content': f'Current rolling summary to preserve and refine:\n{self.rolling_summary}',
                }
            )

        summary_messages.append(
            {
                'role': 'user',
                'content': 'Conversation block to incorporate:\n' + '\n'.join(lines),
            }
        )

        response = self.client.chat(
            model=self.model,
            messages=summary_messages,
            stream=False,
        )
        return response['message']['content'].strip()

    def build_model_messages(self):
        payload = [{'role': 'system', 'content': self.system_prompt}]

        if self.rolling_summary:
            payload.append(
                {
                    'role': 'system',
                    'content': (
                        'Rolling summary of earlier conversation context '\
                        f'(covers messages 1 through {self.summarized_through_message}):\n'
                        f'{self.rolling_summary}'
                    ),
                }
            )

        for msg in self._unsummarized_messages():
            payload.append({'role': msg['role'], 'content': msg['content']})

        return payload

    def resumed_context_lines(self):
        lines = []

        if self.rolling_summary and self.summarized_through_message > 0:
            lines.append(
                'SUMMARY'
                f'[1-{self.summarized_through_message}]: {self.rolling_summary}'
            )

        for msg in self._unsummarized_messages():
            lines.append(f"{msg['role'].upper()}[{msg['index']}]: {msg['content']}")

        return lines

    def generate_assistant_response(self):
        model_messages = self.build_model_messages()
        stream = self.client.chat(model=self.model, messages=model_messages, stream=True)

        chunks = []
        print(f'\n{self.assistant_name}: ', end='', flush=True)

        spinner_stop = threading.Event()
        spinner_started = threading.Event()
        spinner_frames = cycle('|/-\\')

        def _spinner():
            spinner_started.set()
            while not spinner_stop.is_set():
                print(f'\r{self.assistant_name}: Thinking... {next(spinner_frames)}', end='', flush=True)
                sleep(0.1)
            print(f'\r{self.assistant_name}: ', end='', flush=True)

        spinner_thread = threading.Thread(target=_spinner, daemon=True)
        spinner_thread.start()
        spinner_started.wait(timeout=0.1)

        spinner_active = True
        for chunk in stream:
            text = chunk.get('message', {}).get('content', '')
            if text:
                if spinner_active:
                    spinner_stop.set()
                    spinner_thread.join(timeout=0.3)
                    spinner_active = False
                print(text, end='', flush=True)
                chunks.append(text)
        if spinner_active:
            spinner_stop.set()
            spinner_thread.join(timeout=0.3)
        print('')
        return ''.join(chunks).strip()

    def close(self):
        self.status = 'closed'
        self.ended_at = self._now_iso()
        self.updated_at = self.ended_at
        self.save()

    def save(self):
        self.updated_at = self._now_iso()
        payload = {
            'session_id': self.session_id,
            'model': self.model,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'ended_at': self.ended_at,
            'status': self.status,
            'messages': self.messages,
            'summaries': self.summaries,
            'rolling_summary': self.rolling_summary,
            'summarized_through_message': self.summarized_through_message,
            'unsummarized_message_indexes': [
                m['index'] for m in self._unsummarized_messages()
            ],
        }

        folder = os.path.dirname(self.output_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)

    def _load_from_file(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f'Resume file not found: {path}')

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError('Malformed YAML: root must be a mapping/object.')

        required = ['session_id', 'model', 'created_at', 'status', 'messages']
        for key in required:
            if key not in data:
                raise ValueError(f'Malformed YAML: missing required field "{key}".')

        self.session_id = data['session_id']
        self.model = data.get('model', self.model)
        self.created_at = data['created_at']
        self.updated_at = data.get('updated_at', self._now_iso())
        self.ended_at = data.get('ended_at')
        self.status = 'active'
        self.messages = data.get('messages', [])
        self.summaries = data.get('summaries', [])
        self.rolling_summary = data.get('rolling_summary', '')
        self.summarized_through_message = data.get('summarized_through_message', 0)

        if not isinstance(self.messages, list):
            raise ValueError('Malformed YAML: messages must be a list.')
        if not isinstance(self.summaries, list):
            raise ValueError('Malformed YAML: summaries must be a list.')

    @staticmethod
    def _now_iso():
        return datetime.now(timezone.utc).isoformat()
