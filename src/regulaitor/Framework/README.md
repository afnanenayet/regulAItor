# FDA Warning Letter Processing System

## Running

### Prerequisites

* Install [docker](https://www.docker.com/)
* Run `qdrant` using the instructions to [run locally](https://qdrant.tech/documentation/quickstart/)
* Create a JSON file with the autogen config. This should have 
  your OpenAI API credentials and will look like the file called `OAI_CONFIG_LIST`
  in this directory.
* Run the example script with `uv run warning-letter-state-machine-example`

## Workflow

1. **Initialization**: Start of the warning letter processing
2. **Input Validation**: Check if the input is a valid FDA warning letter
3. **Summary Extraction**: Generate a concise summary of key violations
4. **Similar Cases Retrieval**: Find and analyze related past warning letters
5. **Regulation Extraction**: Identify specific regulatory violations
6. **Law Content Retrieval**: Fetch detailed law and regulation information
7. **Corrective Action Generation**: Develop comprehensive compliance strategies
8. **Review and Validation**: Iteratively refine and validate corrective actions
9. **Finalization**: Complete processing of the warning letter
