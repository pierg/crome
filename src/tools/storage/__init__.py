import os
import pickle
from pathlib import Path
from graphviz import Source


class Store:
    output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output'))

    @staticmethod
    def save_to_file(text: str, file_name: str, output_folder_name=None, absolute_folder_path=None):

        if Path(file_name).suffix == "":
            file_name += ".txt"

        if absolute_folder_path is not None:
            output_folder = absolute_folder_path
        else:
            if output_folder_name is not None:
                output_folder = f"{Store.output_folder}/{output_folder_name}"
            else:
                output_folder = f"{Store.output_folder}"

        output_file = f"{output_folder}/{file_name}"
        output_file_orig = f"{output_folder}/{file_name}"

        output_folder = Path(output_folder)
        output_file = Path(output_file)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with open(output_file, 'w') as f:
            f.write(text)

        f.close()
        return output_file_orig

    @staticmethod
    def generate_eps_from_dot(dot_mealy: str, file_name: str, folder_name=None):

        Store.save_to_file(dot_mealy, f"{file_name}_dot.txt", folder_name)

        if folder_name is not None:
            output_folder = f"{Store.output_folder}/{folder_name}"
        else:
            output_folder = f"{Store.output_folder}"

        output_folder = Path(output_folder)

        source = Source(dot_mealy, directory=output_folder, filename=file_name, format="eps")
        source.render(cleanup=True)
        print(f"{output_folder}/{file_name} -> DOT and EPS files generated")



