import os

data = {
    'feature': 'Vixen Environment',
    'current_path': os.path.dirname(os.path.abspath(__file__)),
    'vixen_environment_install_path': '/opt/vixen-env',
    'executable_install_path': '/usr/bin',
    'executable_name': 'vixen-manager',
    'executable_patch': '#!/opt/vixen-env/bin/python'
}

setup = {
    'purpose': f"Install {data['feature']}",
    'tasks': [
        {
            'purpose': f"Create the Vixen environment to '{data['vixen_environment_install_path']}'",
            'process_command': f"sudo python -m venv {data['vixen_environment_install_path']}",
            'cancel_command': f"sudo rm -r {data['vixen_environment_install_path']}",
            'requirements': [
                {
                    'purpose': 'Check an existing installation',
                    'callback': lambda: not os.path.isdir(data["vixen_environment_install_path"]),
                    'failure_details': f"{data['feature']} is already installed"
                }
            ]
        }
    ]
}