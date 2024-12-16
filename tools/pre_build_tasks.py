###################################################################################################################################################### 
##
##    This script was originally produced for the GitHub repo provided below under the "Do WHat You Want With It" license.
##
##    Repo: https://github.com/viksmir/project_template
##
###################################################################################################################################################### 



import sys
import tempfile
import argparse
import subprocess
from pathlib import Path



######################################################################################################################################################
##  Helper methods  ##################################################################################################################################
######################################################################################################################################################



def execute_iwyu(args):
    print(f'Executing IWYU ...')
    
    #iwyu_scan_command = f'python3.11 C:/msys64/ucrt64/bin/iwyu_tool.py -v -p {args.bin_dir}/compile_commands.json 2> {args.bin_dir}/iwyu.log'
    #        
    #with open(f'{args.bin_dir}/iwyu_scan_out.txt', 'w') as iwyu_scan_result_file:
    #    iwyu_scan_result_file.write(f'COMMAND: {iwyu_scan_command}\n')
    #    iwyu_scan_result_file.flush()
    #    
    #    iwyu_scan_result = subprocess.run(iwyu_scan_command, stdout=iwyu_scan_result_file, shell=True)
    #
    #    if (iwyu_scan_result.returncode != 0):
    #        print(f'...... IWYU scan ERROR, error log available at {iwyu_scan_result_file.name} ...')
    #        exit(-1)
    #    
        
    iwyu_cleanup_command = f'python3.11 C:/msys64/ucrt64/bin/fix_includes.py --nosafe_headers --ignore_re "{args.bin_dir}(/extern/|\\extern\\).*" {args.bin_dir}/iwyu.log'
    
    with open(f'{args.bin_dir}/iwyu_cleanup_out.txt', 'w') as iwyu_cleanup_result_file:
        iwyu_cleanup_result_file.write(f'COMMAND: {iwyu_cleanup_command}\n')
        iwyu_cleanup_result_file.flush()
        
        iwyu_cleanup_result = subprocess.run(iwyu_cleanup_command, stdout=iwyu_cleanup_result_file, shell=True)
        
        if (iwyu_cleanup_result.returncode != 0):
            print(f'...... IWYU clean-up ERROR, error log available at {iwyu_cleanup_result_file.name} ...')
            exit(-1)

    print(f'... DONE')
    pass



def execute_clang_format(args):
    print(f'Executing Clang-Format ...')
    
    source_argument = args.source_files.replace(',', ' ')
    
    command = f'clang-format -style=file:{Path(args.style_file).absolute().as_posix()} -i {source_argument}'
    
    with open(f'{args.bin_dir}/clang_format_out.txt', 'w') as clang_format_output_file:
        with open(f'{args.bin_dir}/clang_format_err.txt', 'w') as clang_format_error_file:
            clang_format_result = subprocess.run(command, stdout=clang_format_output_file, stderr=clang_format_error_file)
        
            if (clang_format_result.returncode == 0):
                print(f'...... Clang-Format clean-up OK, log: {clang_format_output_file.name}')
            else:
                print(f'...... Clang-Format clean-up ERROR, error log available at {clang_format_error_file.name} ...')
                exit(-1)

    print(f'... DONE')
    pass



######################################################################################################################################################
##  Main logic  ######################################################################################################################################
######################################################################################################################################################



# Define argument parser
parser = argparse.ArgumentParser(
                    prog='File search and copy helper script.',
                    description='Copies either a single file, or multiple files by search (either by extensions or glob query).')

parser.add_argument('-b',             '--bin_dir',       action='store',      required=True,   help='Output of all generated files for the build (equivalent to CMAKE_CURRENT_BINARY_DIR)')                                          
parser.add_argument('-i',             '--include_dirs',  action='store',      required=True,   help='Include directories against which to perform search for includes during analysis')
parser.add_argument('-s',             '--source_files',  action='store',      required=True,   help='C++ header and source files to analyze')
parser.add_argument('--std',          '--std',           action='store',      required=True,   help='C++ standard used in the code')
parser.add_argument('--mapping_file', '--mapping_file',  action='store',      required=False,  help='Path to the IWYU mapping file')
parser.add_argument('--style_file',   '--style_file',    action='store',      required=False,  help='Path to the Clang Format style file')

args = parser.parse_args()



# Execute Include What You Use
execute_iwyu(args)


# Execute Clang Format
execute_clang_format(args)


print(f'COMPLETE: Finished processing files')
exit(0)