from typing import Dict, Optional
from pathlib import Path
import click

import toml
from jsonschema import validate, ValidationError


SCHEMA = {
  'type': 'object',
  'properties': {
    'profile': { '$ref': '#/definitions/Profiles' },
  },
  'additionalProperties': False,
  'definitions': {
    'Profile': {
      'type': 'object',
      'properties': {
        'url': {
          'type': 'string',
        },
        'email': {
          'type': 'string',
        },
      },
      'required': ['url'],
      'additionalProperties': False,
    },

    'Profiles': {
      'type': 'object',
      'additionalProperties': {
        '$ref': '#/definitions/Profile'
      },
    },
  },
}


class Profile:
    @classmethod
    def from_dict(cls, data) -> 'Profile':
        return cls(data['url'], data.get('email'))

    def __init__(self, url: str, email: Optional[str] = None):
        self.url = url
        self.email = email


class Configuration:
    @classmethod
    def load(cls) -> 'Configuration':
        path = Path.home() / '.config' / 'goji' / 'config.toml'
        if path.exists():
            return cls.fromfile(path)

        return cls({})

    @classmethod
    def fromfile(cls, path: Path) -> 'Configuration':
        with open(path) as fp:
            data = toml.load(fp)

        try:
            validate(instance=data, schema=SCHEMA)
        except ValidationError as exception:
            message = 'Invalid config in {}, at path /{}, {}'.format(
                path,
                '/'.join(exception.path),
                exception.message
            )
            raise click.ClickException(message)

        profiles: Dict[str, Profile] = {}
        for (profile, data) in data.get('profile', {}).items():
            if profile.lower() in profiles:
                raise click.ClickException(f'Profile {profile} defined more than once')

            profiles[profile] = Profile.from_dict(data)

        return cls(profiles=profiles)

    def __init__(self, profiles: Dict[str, Profile]):
        self.profiles = profiles
