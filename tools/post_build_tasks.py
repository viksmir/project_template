import os
import glob
import shutil
import argparse
import subprocess
from pathlib import Path


# Define argument parser
parser = argparse.ArgumentParser(
                    prog='File search and copy helper script.',
                    description='Copies either a single file, or multiple files by search (either by extensions or glob query).')

parser.add_argument('-o', '--out_dir',    action='store',      required=True,  help='Output directory')                                        
parser.add_argument('-b', '--bin_dir',    action='store',      required=True,  help='Output of all binary files for the build (equivalent to CMAKE_CURRENT_BINARY_DIR)')                                          
parser.add_argument('-p', '--proj',       action='store',      required=False, help='Comma-separated projects in the build')
parser.add_argument('-t', '--test_proj',  action='store',      required=False, help='Comma-separated test projects in the build')
parser.add_argument('-c', '--coverage',   action='store_true', required=False, help='Attempt to perform coverage analysis on the test projects')

args = parser.parse_args()

args.out_dir = Path(os.path.abspath(args.out_dir)).as_posix() if (args.out_dir is not None) else None
args.bin_dir = Path(os.path.abspath(args.bin_dir)).as_posix() if (args.bin_dir is not None) else None



project_list      = [s.strip() for s in args.proj.split(',')      if (len(s) > 0)]
test_project_list = [s.strip() for s in args.test_proj.split(',') if (len(s) > 0)]






def copy_files(out_dir, clear=False, file=None, src_dir=None, extensions=None, recursive=False, keep_paths=False, shrink=False, ignore=False):
    # Update output and source directories to ensure they are using full system paths
    out_dir = Path(os.path.abspath(out_dir)).as_posix() if (out_dir is not None) else None
    src_dir = Path(os.path.abspath(src_dir)).as_posix() if (src_dir is not None) else None

    # Perform check on mutually exclusive conditions
    if (file is not None) and (extensions is not None):
        raise SystemExit(f'ERROR: specify either -f (a file) or -e (file extensions), leaving...')

    # Copy the single file if requested
    if (file is not None):
        if (os.path.isfile(file) == False):
            raise SystemExit(f'COMPLETE: file not found at {file}, leaving...')
        
        # Create new directory if needed
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        
        # Copy the file to the output directory
        if (clear):
            if os.path.exists(out_dir):
                if (os.path.isdir(out_dir) == False):
                    raise SystemExit(f'ERROR: output path "{out_dir}" is a file, leaving...')
                shutil.rmtree(out_dir)
        final_dist = shutil.copy2(file, out_dir)
        
        # Log the result
        print(f'File copy complete: finished copying {Path(file).as_posix()} to {Path(final_dist).as_posix()}')
        return

    # Copy multiple files based on the search results
    if (extensions is not None):
        extensions_list = [s.strip() for s in extensions.split(',') if (len(s) > 0)]
        
        if (len(extensions_list) == 0):
            raise SystemExit(f'ERROR: invalid extensions list, leaving...')

        files_to_copy = list()
        unique_file_names = dict()
        for extension in extensions_list:
            # Find all files            
            if (recursive):
                glob_results = Path(f'{src_dir}').rglob(f'*.{extension}')
            else:
                glob_results = Path(f'{src_dir}').glob(f'*.{extension}')
                            
            # Process all files
            for in_file in glob_results:
                in_file = Path(in_file).as_posix()
                
                # Check if file, if not, continue
                if (os.path.isfile(in_file) == False):
                    continue
                
                # File path relative to the search directory if needed
                file_name = os.path.basename(in_file)
                relative_path = in_file.replace(src_dir, '')
                if (keep_paths):
                    if (shrink):
                        relative_path = relative_path.replace('/', '_')
                    out_file = Path(f'{out_dir}/{relative_path}').as_posix()
                else:
                    out_file = Path(f'{out_dir}/{file_name}').as_posix()
                
                # Save the entry
                files_to_copy.append([file_name, relative_path, in_file, out_file])
                
                # Keep the record of unique names to avoid overwritting under certain conditions
                if (file_name in unique_file_names):
                    if (keep_paths == False):
                        raise SystemExit(f'ERROR: file "{file_name}" was found in multiple directories relative to {src_dir}, leaving...')
                else:
                    unique_file_names[file_name] = None

        # Create new directory if needed
        if (clear):
            if os.path.exists(out_dir):
                if (os.path.isdir(out_dir) == False):
                    raise SystemExit(f'ERROR: output path "{out_dir}" is a file, leaving...')
                shutil.rmtree(out_dir)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        
        # Perform initial checks
        for [file_name, relative_path, in_file, out_file] in files_to_copy:
            if (os.path.isdir(out_file)):
                raise SystemExit(f'ERROR: output path "{out_file}" already exists and is a directory, leaving...')
            
            if (os.path.isfile(out_file) and (ignore == False)):
                raise SystemExit(f'ERROR: output file "{out_file}" already exists, leaving...')

        # Copy files
        files_copied = []
        for [file_name, relative_path, in_file, out_file] in files_to_copy:
            try:
                Path(os.path.dirname(out_file)).mkdir(parents=True, exist_ok=True)
                shutil.copyfile(in_file, out_file)
                files_copied.append(relative_path)
                print(f'PROGRESS: copied [src_dir]{relative_path} to {out_file}')
            except Exception as e:
                raise SystemExit(f'ERROR: could not copy [src_dir]{relative_path} due to the following error "{e}", leaving...')

        print(f'File copy complete: finished copying {len(files_copied)} files')
        return


    print(f'WARNING: leaving with no action performed')
    return






def process_project(args, project_name, test_proj):
    print(f'Processing "{project_name}" project ...')

    # Copying all the generated binaries and report files
    print(f'... copying the binaries ...')
    copy_files(out_dir=args.out_dir, src_dir=f'{args.bin_dir}/{project_name}', extensions='exe,dll,pdb')
    
    if (test_proj) and (args.coverage):
        # Execute the unit test to generate coverage metadata
        print(f'... executing the coverage binaries ...')
        with open(f'{args.bin_dir}/{project_name}/{project_name}_out.txt', 'w') as output_file:
            with open(f'{args.bin_dir}/{project_name}/{project_name}_err.txt', 'w') as error_file:
                executable_path = f'{args.bin_dir}/{project_name}/{project_name}.exe'
                if (os.path.exists(executable_path) == False):
                    print(f'WARNING: executable {executable_path} could not be found, leaving with no action performed')
                    return
                subprocess.run([executable_path], stdout=output_file, stderr=error_file)

        # Copy all RELEVANT coverage metadata files to the buffer directory
        print(f'... copying coverage metadata ...')
        copy_files(out_dir=f'{args.bin_dir}/{project_name}/coverage_metadata', src_dir=f'{args.bin_dir}/{project_name}/CMakeFiles/{project_name}.dir/',        clear=True, recursive=False, keep_paths=True, shrink=False, extensions='gcno,gcda')
        copy_files(out_dir=f'{args.bin_dir}/{project_name}/coverage_metadata', src_dir=f'{args.bin_dir}/{project_name}/CMakeFiles/{project_name}.dir/__/src/', clear=True, recursive=True,  keep_paths=True, shrink=False, extensions='gcno,gcda')
        
        # Generate coverage report
        print(f'... generating coverage report ...')
        with open(f'{args.bin_dir}/{project_name}/{project_name}_gcovr_out.txt', 'w') as output_file:
            with open(f'{args.bin_dir}/{project_name}/{project_name}_gcovr_err.txt', 'w') as error_file:
                Path(f'{args.out_dir}/coverage_report').mkdir(parents=True, exist_ok=True)
                result = subprocess.run(['gcovr',
                                         '--root', '.',
                                         '--html', '--html-details',
                                         '--output', f'{args.out_dir}/coverage_report/coverage_report.html',
                                         '--object-directory', f'{args.bin_dir}/{project_name}/coverage_metadata',
                                         '--exclude-directories', './extern',
                                         '-j', '12', '--verbose'],
                                             stdout=output_file,
                                             stderr=error_file)
                if (result):
                    print(f'...... generation ok, coverage report available at {args.out_dir}/coverage_report/coverage_report.html ...')
                else:
                    print(f'...... generation error, error log available at {error_file} ...')
        
    print(f'... DONE')
    pass






# Clean the output directory
if os.path.exists(args.out_dir):
    if (os.path.isdir(args.out_dir) == False):
        raise SystemExit(f'ERROR: output path "{args.out_dir}" is a file, leaving...')
    shutil.rmtree(args.out_dir)
Path(args.out_dir).mkdir(parents=True, exist_ok=True)






for project in project_list:
    process_project(args, project, test_proj=False)






for project in test_project_list:
    process_project(args, project, test_proj=True)






print(f'COMPLETE: Finished processing projects')
exit(0)