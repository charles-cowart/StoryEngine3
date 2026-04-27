import argparse
import sys

from ollama import ResponseError

from session import Session


def parse_args():
    parser = argparse.ArgumentParser(
        description='Interactive story-writing CLI using Ollama with YAML session persistence.'
    )
    parser.add_argument('--model', default='gpt-oss:20b', help='Model name (default: gpt-oss:20b)')
    parser.add_argument('--resume', help='Path to an existing YAML session file to resume')
    parser.add_argument('--output', help='Output path for YAML session file')
    return parser.parse_args()


def run_loop(session):
    print('Story session started.')
    print(f'Model: {session.model}')
    print(f'Session file: {session.output_path}')
    print('Type your prompt, or enter /quit to save and exit.\n')

    while True:
        try:
            user_input = input('You: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting and saving session...')
            session.close()
            return

        if not user_input:
            # For story writing, if the user presses return, consider that a command
            # to continue writing on the same course.
            user_input = 'continue'

        if user_input.lower() in ['/quit', '/exit']:
            print('Saving session...')
            session.close()
            print(f'Session saved to {session.output_path}')
            return

        session.add_user_message(user_input)

        try:
            assistant_reply = session.generate_assistant_response()
        except ResponseError as err:
            print(f'\nOllama model error: {err}')
            print('Your message has been kept in the log. You can continue or quit.')
            continue
        except Exception as err:
            print(f'\nUnexpected error talking to Ollama: {err}')
            print('Your message has been kept in the log. You can continue or quit.')
            continue

        session.add_assistant_message(assistant_reply)


def main():
    args = parse_args()

    try:
        session = Session(model=args.model, output_path=args.output, resume_path=args.resume)
    except FileNotFoundError as err:
        print(err)
        sys.exit(1)
    except ValueError as err:
        print(f'Unable to resume session: {err}')
        sys.exit(1)
    except Exception as err:
        print(f'Failed to initialize session: {err}')
        sys.exit(1)

    try:
        run_loop(session)
    except Exception as err:
        print(f'Fatal runtime error: {err}')
        print('Attempting to save session before exit...')
        try:
            session.close()
        except Exception as save_err:
            print(f'Failed to save session: {save_err}')
        sys.exit(1)


if __name__ == '__main__':
    main()
