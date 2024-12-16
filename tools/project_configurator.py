###################################################################################################################################################### 
##
##    This script was originally produced for the GitHub repo provided below under the "Do WHat You Want With It" license.
##
##    Repo: https://github.com/viksmir/project_template
##
###################################################################################################################################################### 



import os
import sys
import stat
import json
import glob
import shutil
import hashlib
import urllib.request
import argparse
import subprocess
from re import L
from pathlib import Path



######################################################################################################################################################
##  Helper methods  ##################################################################################################################################
######################################################################################################################################################



def ExitWithError(message):
    print(message)
    sys.exit(message)



def RemoveReadOnly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)
    


def CheckTool(executable, version_string=None):
    output = subprocess.run(f'{executable} --version', capture_output=True, shell=True)
    
    if (output.returncode != 0):
        ExitWithError(f'\tERROR: {executable} is not available, leaving...')
    else:
        version = output.stdout.decode('ascii')
        
        if (version_string is not None):            
            if (version_string not in version):
                ExitWithError(f'\tERROR: executable "{executable}" does not match the version requirements, please install {version_string}, leaving...')

        print(f'\tFound: {version.replace('\r\n','').replace('\n','')}')



def ResetDirectory(folder):
    folder_path = Path(os.path.abspath(folder)).as_posix()
    
    if (os.path.isfile(folder_path)):
        raise ExitWithError(f'\tERROR: External folder path "{folder_path}" already exists and is a file, leaving...')
    else:
        if (os.path.exists(folder_path)):
            shutil.rmtree(folder_path, onexc=RemoveReadOnly)
        os.makedirs(folder_path)
        print(f'\t{folder_path} - OK')



def FetchGitRepo(git_dir, name, repo, hash):
    git_dir = Path(os.path.abspath(git_dir + f'./{name}')).as_posix()
    
    if (os.path.exists(git_dir)):
        ExitWithError(f'\tERROR: Failed to clone repo "{name}", target directory "{git_dir}" alredy exists, leaving...')
    
    if (hash is None):
        output = subprocess.run(f'git clone {repo} {git_dir}', capture_output=True, shell=True)
    else:
        output = subprocess.run(f'git clone {repo} {git_dir} && cd {git_dir} && git checkout {hash}', capture_output=True, shell=True)

    if (output.returncode == 0):
        print(f'\tRepo "{name}" cloned to {git_dir}')
    else:
        ExitWithError(f'\tERROR: Failed to clone repo "{name}" with error {output.stderr}, leaving...')



def FetchWgetResource(wget_dir, name, url, md5=None, sha256=None):
    wget_dir = Path(os.path.abspath(wget_dir + f'./{name}')).as_posix()
    filename = os.path.basename(url)
    file_path = f'{wget_dir}/{filename}'

    if (os.path.exists(wget_dir)):
        ExitWithError(f'\tERROR: Failed to download resource "{name}", target directory "{wget_dir}" alredy exists, leaving...')

    try:
        os.mkdir(f'{wget_dir}')
        urllib.request.urlretrieve(url, f'{file_path}')
    except Exception as e:
        ExitWithError(f'\tERROR: Failed to download resource "{name}" with error {e}, leaving...')

    try:
        if (md5 is not None):
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as file:
                for byte_block in iter(lambda: file.read(4096), b""):
                    md5_hash.update(byte_block)
        
            md5_hash = md5_hash.hexdigest()
            
            if (md5_hash != md5):
                ExitWithError(f'\tERROR: Failed to download resource "{name}", MD5 mismatch, leaving...')

        if (sha256 is not None):
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as file:
                for byte_block in iter(lambda: file.read(4096), b""):
                    sha256_hash.update(byte_block)
        
            sha256_hash = sha256_hash.hexdigest()
            
            if (sha256_hash != sha256):
                ExitWithError(f'\tERROR: Failed to download resource "{name}", SHA256 mismatch, leaving...')
        
        output = subprocess.run(f'tar -xvf {file_path} -C {wget_dir}', capture_output=True, shell=True)
        if (output.returncode != 0):
            ExitWithError(f'\tERROR: Could not unpack the "{name}" ({file_path}) with error {e}, leaving...')
        
        os.remove(file_path)
        
        print(f'\tResource "{name}" downloaded to {wget_dir}')

    except Exception as e:
        ExitWithError(f'\tERROR: Failed to download resource "{name}" with error {e}, leaving...')
    
    

def RemoveEntry(base_dir, entry):
    entry_dir = Path(os.path.abspath(base_dir + f'./{entry}')).as_posix()
    
    matches = glob.glob(entry_dir, include_hidden=True)
    
    for match in matches:
        if (os.path.isfile(match)):
            os.remove(match)
            
        if (os.path.isdir(match)):
            shutil.rmtree(match)
            
    print(f'\tProcessed: {entry}')
            


        
######################################################################################################################################################
##  Main logic  ######################################################################################################################################
######################################################################################################################################################



# Define argument parser
parser = argparse.ArgumentParser(
                    prog='File search and copy helper script.',
                    description='Copies either a single file, or multiple files by search (either by extensions or glob query).')
                         
parser.add_argument('-f', '--file', action='store', required=True, help='File containing requirements packaged into JSON')                                        

args = parser.parse_args()



# Checking arguments
if (args.file is None) or (args.file == ''):
    ExitWithError(f'\tERROR: specify --file (requirements JSON file), leaving...')
else:
    file_path = Path(os.path.abspath(args.file)).as_posix()

    with open(file_path, 'r') as file:
        requirements_data = json.load(file)


    
# Checking external tools
print('\n\rSCANNING FOR EXTERNAL TOOLS...')
for tool in [{'executable':'git'}] +\
            [{'executable':'cmake'}] +\
            [{'executable':'gcovr'}] +\
            [{'executable':'ninja'}] +\
            [{'executable':'bsdtar'}] +\
            [{'executable':'python3.11'}] +\
            requirements_data['tools']:
    executable      = tool['executable'] if 'executable' in tool else None
    version_string  = tool['version_string'] if 'version_string' in tool else None

    if (executable is None):
        ExitWithError(f'\tERROR: The requirement file contains undefined executable, please ensure all executables provide the NAME field, leaving...')

    CheckTool(executable, version_string)



# Resetting local directories
print('\n\rRESETTING LOCAL DIRECTORIES...')
for reset in requirements_data['reset']:
    ResetDirectory(f'./{reset['folder']}')



# Fetching GIT repositories
print('\n\rFETCHING GIT DIRECTORIES...')
for git_repo in requirements_data['git']:
    name    = git_repo['name'] if 'name' in git_repo else None
    repo    = git_repo['repo'] if 'repo' in git_repo else None
    hash    = git_repo['hash'] if 'hash' in git_repo else None

    if (name is None) or (repo is None):
        ExitWithError(f'\tERROR: The requirement file contains GIT infos without name or repo fields, please ensure all GIT entries provide both NAME and REPO fields, leaving...')

    FetchGitRepo(f'./{requirements_data['git_dir']}', name, repo, hash)



# Fetching WGET resources
print('\n\rFETCHING WGET RESOURCES...')
for wget_resource in requirements_data['wget']:
    name    = wget_resource['name']   if 'name'   in wget_resource else None
    url     = wget_resource['url']    if 'url'    in wget_resource else None
    md5     = wget_resource['md5']    if 'md5'    in wget_resource else None
    sha256  = wget_resource['sha256'] if 'sha256' in wget_resource else None

    if (name is None) or (url is None):
        ExitWithError(f'\tERROR: The requirement file contains WGET infos without name or url fields, please ensure all WGET entries provide both NAME and URL fields, leaving...')
        
    FetchWgetResource(f'./{requirements_data['wget_dir']}', name, url, md5, sha256)



# Removing entries
print('\n\rREMOVING ENTRIES...')
for entry in requirements_data['delete']:
    if (entry == ""):
        ExitWithError(f'\tERROR: The requirement file contains empty DELETE entries, leaving...')
        
    RemoveEntry('./', entry)