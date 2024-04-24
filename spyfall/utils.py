import yaml

def load_game_config(config_path: str):
    """
    Loads game configuration from a YAML file.
    
    Args:
        config_path (str): The path to the YAML configuration file.
        
    Returns:
        dict: The loaded game configuration.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

