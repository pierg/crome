# crome-cgg

**Contract-Based Goal Graph**

The tool helps the designer model and deploy robotic missions using contracts. The designer can model the environment, and the goals that the robot must achieve using LTL or Specification Patterns. The tool analyze the goals, build the CGG (a graph of contracts) and realize the controllers via reactive synthesis and simulate the robotic mission.


[Contract for System Design](https://hal.inria.fr/hal-0o0757488/file/RR-8147.pdf)


## Getting Started

Follow these steps to set up and run the project:

### Setup Environment


> NOTE: Conda for Mac with Apple Silicon
>
> Some of the packages in conda do not support arm64 architecture. To install all the dependencies correctly on a Mac with Apple Silicon, make sure that you are running conda for x86_64 architecture.
>
> You can install miniconda for MacOSX x86_64 by running the following commands
>
> ```bash
> curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh > Miniconda3-latest-MacOSX-x86_64.sh
> ```
>
> ```bash
> sh Miniconda3-latest-MacOSX-x86_64.sh
> ```


1. **Create Conda Environment**:

    ```bash
    conda env create -f environment.yml -p .venv
    ```

2. **Activate Conda Environment**:

    ```bash
    conda activate ./.venv
    ```

3. **Install Poetry Dependencies**:

    ```bash
    poetry install
    ```

### Running the Project

Once the environment is set up, you can run your project using your preferred method.

### Visual Studio Code Setup

1. Open the project in VSCode.
2. Set Python Interpreter:

   - Use the Command Palette (Ctrl+Shift+P).
   - Type "Python: Select Interpreter".
   - Choose the interpreter located in the `.venv` folder.

## Additional Notes

- Make sure to activate the Conda environment before running the project or installing additional dependencies.
- Update or modify the project's dependencies in `pyproject.toml` and `environment.yml` as necessary.
