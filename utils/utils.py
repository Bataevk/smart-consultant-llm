import os
from dotenv import load_dotenv

def load_keys():
    file_path = os.environ['VIRTUAL_ENV']

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('')  # create empty file

    load_dotenv(os.path.join(file_path, 'API_keys.env'))

def save_keys():
    file_path = os.environ['VIRTUAL_ENV']

    env_dict = os.environ

    with open(os.path.join(file_path, 'API_keys.env'), 'w') as envfile:
        for key, value in env_dict.items():
            if key.endswith('_API_KEY'):
                envfile.write(f"{key} = {value}\n")




def set_keys(array):
    ''' Set the keys of an array with names as environment variables'''
    if not 'y' in input('do you want to set API keys? (y/n):').strip().lower():
        return
    

    # Step 1: Define the list of names
    names = list(map(lambda x: x + '_API_KEY', array))

    while True:
        try:
            # Step 2: Ask the user for an index
            index_input = input("{}\nEnter an number (1-{}) or 'done' to continue: ".format( '\n'.join(map(lambda x: f'{x[0]}. {x[1]}', enumerate(names, 1))), len(names) )).strip()
            
            # Check if the user wants to exit
            if index_input.lower() == 'done':
                print("continue main program")
                break

            index = int(index_input) - 1

            # Step 3: Get the name by index
            env_var_name = names[index]
            
            # Step 4: Ask the user for a value
            value = input(f"Enter a value for the environment variable {env_var_name}: ")

            # Step 5: Set the value to the environment variable
            os.environ[env_var_name] = value

            print(f"The environment variable {env_var_name} has been set to {value}")

        except ValueError:
            print("Error: Please enter a valid number.")
        except IndexError as e:
            print(f"Error: {e}")
