# Deploy script entrypoint
import os
import shutil
import zipfile
import zlib
from build_helpers import *

def deploy():
    """Deploy packages"""
    build_data = get_build_data()
    version_data = get_version_file_info(build_data["mod_name"])
    changelog = get_changelog()
    print(f"Deploying {build_data['mod_name']} version {get_version(version_data)}\n=================")
    print(f"Changes:\n{changelog}")

if __name__ == "__main__":
    deploy()
