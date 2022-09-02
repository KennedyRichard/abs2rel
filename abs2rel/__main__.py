"""Turn local absolute imports into relative ones."""

### standard library imports

from pathlib import Path

from os.path import relpath


def abs2rel():

    ### notify user of nature of changes to be made

    print(
      "We are about to perform destructive changes"
      " in the python files in this directory tree."
      " Are you sure you want to proceed? y/n"
    )

    answer = input()

    if answer.lower() != 'y':

        print("Aborted operation.")
        return

    ### list all existing python files recursively
    all_py_files = tuple(Path('.').rglob('*.py'))

    ### create a map associating each path to a
    ### format where it is divided with a dot notation
    ### as if it were to be absolute-imported

    path_to_abs_dotted_import = {
      path : '.'.join(path.parts[:-1] + (path.stem,))
      for path in all_py_files
    }

    ### create a map from the previous one where the
    ### keys are mapped to the values

    abs_dotted_import_to_path = {

      import_text: path

      for path, import_text
      in path_to_abs_dotted_import.items()

    }

    ### alias path_to_abs_dotted_import values as the
    ### possible local imports

    possible_local_imports = (
      path_to_abs_dotted_import.values()
    )

    ### gather data about all lines in each python file
    ### with imports starting with 'from'

    path_to_import_data = {}

    for path in all_py_files:

        import_data = get_imports_data(
                        path,
                        possible_local_imports
                      )

        if import_data:
            path_to_import_data[path] = import_data

    ###

    for path in all_py_files:

        if path in path_to_import_data:

            replace_imports(
              path,
              path_to_import_data,
              path_to_abs_dotted_import,
              abs_dotted_import_to_path,
            )


def get_imports_data(path, possible_local_imports):

    lines = path.read_text(encoding='utf-8').splitlines()

    import_data = {}

    for line_index, line_text in enumerate(lines):

        statement_data = (

          abs_dotted_import,
          start_char_index,
          end_char_index,

        ) = check_import_data(
              line_text,
              possible_local_imports,
            )

        if abs_dotted_import:
            import_data[line_index] = statement_data

    return import_data


def check_import_data(line_text, possible_local_imports):

    ###

    if line_text.startswith('from '):
        start_char_index = 5

    else: return ('', None, None)

    ###

    if ' import '  in line_text:
        end_char_index = line_text.rindex(' import ')

    elif ' import\\' in line_text:
        end_char_index = line_text.rindex(' import\\')

    elif ' import(' in line_text:
        end_char_index = line_text.rindex(' import(')

    else: return ('', None, None)

    ###

    abs_dotted_import = (
      line_text[start_char_index : end_char_index]
      .replace(' ', '')
    )

    ###

    if abs_dotted_import not in possible_local_imports:
        return ('', None, None)

    ###

    return (
      abs_dotted_import,
      start_char_index,
      end_char_index,
    )


def replace_imports(
      path,
      path_to_import_data,
      path_to_abs_dotted_import,
      abs_dotted_import_to_path,
    ):

    lines = path.read_text(encoding='utf-8').splitlines()

    import_data = path_to_import_data[path]

    for (

      line_index,

      (
        abs_dotted_import,
        start_char_index,
        end_char_index,
      ),

    ) in import_data.items():

        line_text = lines[line_index]

        new_text = 'from '
        tail = line_text[end_char_index:]

        ###

        imported_path = (
          abs_dotted_import_to_path[abs_dotted_import]
        )

        rpath = Path(relpath(imported_path, path))

        rel_dotted_import = (

          '.'.join(

                '' if part == '..' else part

                for part in (
                  rpath.parts[:-1] + (rpath.stem,)
                )

              )
        )

        ###

        new_text = (
          f'from {rel_dotted_import}{tail}'
        )

        lines[line_index] = new_text


    path.write_text(
           '\n'.join(lines),
           encoding='utf-8',
         )


if __name__ == '__main__':
    abs2rel()
