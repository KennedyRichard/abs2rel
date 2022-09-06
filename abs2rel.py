"""Turn local absolute imports into relative ones."""

__version__ = '1.1.0'


### standard library imports

from pathlib import Path

from os.path import relpath

from tokenize import tokenize, NAME

from io import BytesIO


def abs2rel():
    """Convert local absolute imports into relative ones.

    This function must be executed in the top-level
    directory of the package whose imports you want
    to convert.

    This function only converts local imports in
    the 'from ... import ...' format where the 'from'
    and 'import' words are on the same line, which
    satisfy the use-case for which this command
    was created.
    """
    print(f"Executing abs2rel on {Path('.').resolve()}")

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

    print("Calculating needed changes...")

    path_to_import_data = {}

    for path in all_py_files:

        import_data = get_imports_data(
                        path,
                        possible_local_imports
                      )

        if import_data:
            path_to_import_data[path] = import_data

    ### notify user of nature of changes to be made

    no_of_imports = sum(
                      len(imports)
                      for imports
                      in path_to_import_data.values()
                    )

    no_of_files_to_change = len(path_to_import_data)
    no_of_py_files        = len(all_py_files)

    print(
      f"We are about to replace {no_of_imports} imports"
      f" in {no_of_files_to_change} of {no_of_py_files}"
       " python files in this directory tree. Are you sure"
       " you want to proceed? (y/n)"
    )

    answer = input()

    if answer.lower() != 'y':

        print("Aborted operation.")
        return

    ### perform changes

    for path in path_to_import_data:

        replace_imports(
          path,
          path_to_import_data,
          path_to_abs_dotted_import,
          abs_dotted_import_to_path,
        )


def get_imports_data(path, possible_local_imports):
    """Return data about local imports in given path.

    Parameters
    ==========

    path (pathlib.Path)
        path wherein to look for absolute local imports.
    possible_local_imports (dictionary view of values)
        represents the set of the possible local imports
        existing in the package; in other words, if an
        absolute import (pre-formatted in a special way)
        is not present in this dict view, then it cannot
        possibly be a local import.
    """
    ### create dict to store local imports data
    local_imports_data = {}

    ### obtain the file tokens

    tokens = tokenize(

               BytesIO(
                 path
                 .read_text(encoding='utf-8')
                 .encode('utf-8')
               ).readline

             )

    ### create a variable to keep track of the lines where
    ### we find a 'from' keyword
    line_where_found_from = None

    ### iterate over the tokens looking for instances of
    ### the 'from' keyword accompanied by the 'import'
    ### keyword in the same line and record the text
    ### between them that can be considered an
    ### absolute local import

    for (

      token_type,
      string,
      (_, string_start),
      (line_number, string_end),
      line_text,

    ) in tokens:

        ### if we found a 'from' keyword but we are
        ### already in a different line, then we forget
        ### about it completely (since we are not
        ### interested in 'from' and 'imports' that are
        ### not on the same line)

        if (

          line_where_found_from is not None
          and line_number != line_where_found_from

        ):

            line_where_found_from = None

        ### if we didn't find a 'from' keyword before
        ### but encounter one now, store the line number
        ### and the index of the character after the end
        ### of the 'from' keyword (such index represents
        ### the start of the import text between the
        ### 'from' and 'import' keyword)

        if line_where_found_from is None:

            if (

                  token_type == NAME
              and string     == 'from'

            ):

                line_where_found_from = line_number
                import_start_index = string_end + 1

        ### if otherwise we already found a 'from' keyword
        ### and now encounter an 'import' keyword...


        elif (

              token_type == NAME
          and string     == 'import'

        ):
            ## store the index of the character before the
            ## start of the 'import' keyword (such index
            ## represents the end of the import text
            ## between the 'from' and 'import' keyword)
            import_end_index = string_start - 1

            ## isolate the text between the 'from' and
            ## 'import' keywords, without the spaces;
            ## this is the absolute dotted import

            abs_dotted_import = (
              line_text[import_start_index : import_end_index]
              .replace(' ', '')
            )

            ## now we only need to know if the dotted
            ## import is local or not, by checking if it
            ## is inside the set of possible local imports;
            ##
            ## if it is, we store the relevant data
            ## gathered about this local import

            if abs_dotted_import in possible_local_imports:

                ## the line index is the number of the line
                ## where the import is minus one
                line_index = line_where_found_from - 1

                ## store all relevant data associating it
                ## to the line index

                local_imports_data[line_index] = (
                  abs_dotted_import,
                  import_start_index,
                  import_end_index,
                )

            ## regardless of whether or not the import is
            ## local, we reset the variable tracking the
            ## 'from' keyword so we can keep looking for
            ## the next 'from' keyword
            line_where_found_from = None


    ### finally return the data
    return local_imports_data


def replace_imports(
      path,
      path_to_import_data,
      path_to_abs_dotted_import,
      abs_dotted_import_to_path,
    ):
    """Replace imports on given path.

    Parameters
    ==========

    path (pathlib.Path)
        path wherein to replace local absolute by local
        relative imports.
    path_to_import_data (dict)
        associates paths to a dict representing data
        about absolute local imports existent in the path.
    path_to_abs_dotted_import (dict)
        associates paths to the string representing the
        format the paths would assume if they were part of
        a 'from [formatted string here] import ...'
        statement.
    abs_dotted_import_to_path (dict)
        similar to the path_to_abs_dotted_import dict,
        but with keys and values inverted.
    """
    ### retrieve the contents of the path as lines;
    ###
    ### note that line breaks are kept in the lines;
    ### this way, if the file ends with a line break
    ### it is preserved when we concatenated the
    ### lines together to save the file

    lines = (

      path.read_text(encoding='utf-8')
      .splitlines(keepends=True)

    )

    ### retrieve the import data for the path, that is,
    ### data about the absolute local imports it contains
    import_data = path_to_import_data[path]

    ### iterate over each item in the data replacing
    ### absolute local imports by relative ones

    for (

      line_index,

      (
        abs_dotted_import,
        import_start_index,
        import_end_index,
      ),

    ) in import_data.items():

        ## obtain the path represented by the absolute
        ## local import to be replaced

        path_of_absolute_import = (
          abs_dotted_import_to_path[abs_dotted_import]
        )

        ## use such path to obtain yet another version
        ## of it, but relative to the path where the
        ## import statement is
        rpath = Path(relpath(path_of_absolute_import, path))

        ## then, using such relative path, build a string
        ## representing the format this relative path would
        ## assume if it were part of a
        ## 'from [formatted string here] import ...'
        ## statement

        rel_dotted_import = (

          '.'.join(

                '' if part == '..' else part

                for part in (
                  rpath.parts[:-1] + (rpath.stem,)
                )

              )
        )

        ## now that we have the relative local import
        ## properly formatted, we just need to replace
        ## the absolute local import

        # grab the line text
        line_text = lines[line_index]

        # isolate its head, that is, the part of the line
        # before the formatted string ('from' and whatever
        # is before)
        head = line_text[:import_start_index]

        # isolate its tail, that is, the part of the line
        # after the formatted string ('import' and whatever
        # is after)
        tail = line_text[import_end_index:]

        # build the new text of the line by
        # concatenating the head, relative import and
        # tail
        new_text = head + rel_dotted_import + tail

        # then, replace the line text by the new one
        lines[line_index] = new_text


    ### finally, rewrite the file contents;
    ###
    ### note that we don't need to used a line breaking
    ### character in between the lines, because the lines
    ### kept their line breaks when we separated them
    ### at the beginning of this function
    path.write_text(''.join(lines), encoding='utf-8')


if __name__ == '__main__':
    abs2rel()
