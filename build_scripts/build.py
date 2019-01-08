# Build script entrypoint
import os
import shutil
import zipfile
import zlib
from build_helpers import *
from s3_helpers import s3copy
from dependencies import download_dependency

TEMP_PATH = "tmp"
BUILD_PATH = "build"
DEPLOY_PATH = "deploy"
VALID_FILES = ["changelog.txt", "readme.txt"]

def build_nodep_release(version_data, mod_name):
    """Builds the release package with no dependencies"""
    build_path = os.path.join(DEPLOY_PATH,
        f"{mod_name}_Core_" + "{MAJOR}_{MINOR}_{PATCH}.zip".format(**version_data["VERSION"]))
    # with zipfile.ZipFile(build_path, mode='w'):
    #    zipfile.write(os.path.join(BUILD_PATH, "readme.txt", compress_type=zipfile.ZIP_DEFLATED))
    #    zipfile.write(os.path.join(BUILD_PATH, "readme.txt", compress_type=zipfile.ZIP_DEFLATED))
    shutil.make_archive(build_path, 'zip', os.path.join(BUILD_PATH))
    print(f"> Built {build_path}")

def build_full_release(version_data, mod_name):
    """Builds the release package with full dependencies"""
    build_path = os.path.join(DEPLOY_PATH,
        f"{mod_name}_" + "{MAJOR}_{MINOR}_{PATCH}.zip".format(**version_data["VERSION"]))
    shutil.make_archive(build_path, 'zip', os.path.join(BUILD_PATH))
    print(f"> Built {build_path}")

def build_extras(version_data):
    """Builds all Extras packages"""
    for root, dirs, files in os.walk("Extras"):
        for name in dirs:
            build_extra(name, version_data)

def build_extra(name, version_data):
    """Builds a single Extras package"""
    extra_path = os.path.join(DEPLOY_PATH, f"{name}" + "{MAJOR}_{MINOR}_{PATCH}.zip".format(**version_data["VERSION"]))
    print(f"> Building {name}")
    ensure_path(os.path.join(BUILD_PATH,"Extras"))
    ensure_path(os.path.join(BUILD_PATH,"Extras", name))
    shutil.copytree(os.path.join("Extras", name), os.path.join(BUILD_PATH,"Extras", name, "GameData", name))

    shutil.make_archive(extra_path, "zip", os.path.join(BUILD_PATH, "Extras", name))
    print(f"> Built {extra_path}")

def collect_dependencies(dep_data):
    """Finds and downloads all dependencies"""
    #clean_path(TEMP_PATH)
    for name, info in dep_data.items():
        download_dependency(name, info, TEMP_PATH, BUILD_PATH)
    cleanup()

def cleanup():
    onlyfiles = [f for f in os.listdir(BUILD_PATH) if os.path.isfile(os.path.join(BUILD_PATH, f))]
    for f in onlyfiles:
        if f not in VALID_FILES:
            os.remove(os.path.join(BUILD_PATH,f))

def bundle():
    """Builds the set of release packages"""
    # Collect build data
    build_data = get_build_data()
    version_data = get_version_file_info(build_data["mod_name"])

    print(f"Building {build_data['mod_name']} version {get_version(version_data)}\n=================")

    shutil.rmtree(os.path.join(BUILD_PATH, "GameData"), ignore_errors=True)
    shutil.rmtree(os.path.join(BUILD_PATH, "Extras"), ignore_errors=True)
    ensure_path(os.path.join(BUILD_PATH, "GameData"))
    ensure_path(DEPLOY_PATH)

    shutil.copytree(os.path.join("GameData", build_data["mod_name"]), os.path.join(BUILD_PATH, "GameData", build_data["mod_name"]))
    shutil.copy("changelog.txt", os.path.join(BUILD_PATH, "changelog.txt"))
    shutil.copy("readme.txt", os.path.join(BUILD_PATH,  "readme.txt"))

    print(f"Building CORE release package")
    build_nodep_release(version_data, build_data['mod_name'])

    if os.path.exists("Extras"):
      print(f"Building EXTRAS release packages\n")
      build_extras(version_data)

    print(f"Building COMPLETE release package")
    print(f"> Collecting dependencies")

    collect_dependencies(build_data["dependencies"])
    build_full_release(version_data, build_data['mod_name'])

    # Write the version out for Travis deploy scripts to take advantage of
    with open('version.txt', "w") as f:
      f.write(get_version(version_data))

if __name__ == "__main__":
    bundle()
