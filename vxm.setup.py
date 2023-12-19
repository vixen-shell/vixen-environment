"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vxm setup file.
License           : GPL3

Additional Information:
- This file can be considered a template.
"""

import os

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

feature = {
    'name': 'Vixen Environment',
    'install_path': '/opt/vixen-env'
}
feature['install_command'] = f"sudo python -m venv {feature['install_path']}"
feature['remove_command'] = f"sudo rm -r {feature['install_path']}"

library = {
    'name': 'vixen_lib',
    'source': '/opt/vixen-env/bin/activate'
}
library['install_command'] = f"source {library['source']} && sudo pip install --upgrade pip && sudo pip install {CURRENT_PATH}"

executable = {
    'name': 'vxm',
    'install_path': '/usr/bin',
    'patch': '#!/opt/vixen-env/bin/python',
}
executable['install_command'] = f"sudo cp -f {CURRENT_PATH}/{executable['name']} {executable['install_path']}"
executable['remove_command'] = f"sudo rm {executable['install_path']}/{executable['name']}"
executable['patch_command'] = f'sudo sed -i "1s|.*|{executable["patch"]}|" {executable["install_path"]}/{executable["name"]}'

setup = {
    'purpose': f"Install {feature['name']}",
    'tasks': [
        {
            'purpose': 'Create the Vixen environment',
            'process_command': feature['install_command'],
            'requirements': [
                {
                    'purpose': 'Check an existing installation',
                    'callback': lambda: not os.path.isdir(feature['install_path']),
                    'failure_details': f"{feature['name']} is already installed"
                }
            ]
        },
        {
            'purpose': f"Install {library['name']} library",
            'process_command': library['install_command']
        },
        {
            'purpose': 'Remove build folders',
            'process_command': f"sudo rm -r {CURRENT_PATH}/build && sudo rm -r {CURRENT_PATH}/{library['name']}.egg-info",
        },
        {
            'purpose': 'Install Vixen Manager executable',
            'process_command': executable['install_command'],
        },
        {
            'purpose': 'Patch Vixen Manager executable',
            'process_command': executable['patch_command']
        }
    ],
    'status': {
        'initial': True,
        'env_path': feature['install_path'],
        'exec_paths': [f"{executable['install_path']}/{executable['name']}"]
    }
}

update = {
    'purpose': f"Update {feature['name']}",
    'tasks': [
        {
            'purpose': f"Update {library['name']} library",
            'process_command': f"{library['install_command']} --force-reinstall",
            'requirements': [
                {
                    'purpose': 'Check an existing installation',
                    'callback': lambda: os.path.isdir(feature['install_path']),
                    'failure_details': f"{feature['name']} is not installed"
                }
            ]
        },
        {
            'purpose': 'Remove build folders',
            'process_command': f"sudo rm -r {CURRENT_PATH}/build && sudo rm -r {CURRENT_PATH}/{library['name']}.egg-info",
        },
        {
            'purpose': 'Update Vixen Manager executable',
            'process_command': executable['install_command'],
        },
        {
            'purpose': 'Patch Vixen Manager executable',
            'process_command': executable['patch_command']
        }
    ]
}