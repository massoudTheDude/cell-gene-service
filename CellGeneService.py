# Author: Massoud Maher

import json
import pandas as pd
import CellGene
from bottle import route, run, template, request, response
from bottledaemon import daemon_run

cg = CellGene.CellGene('CCLE_protein')

# TODO handle non-existent gene and cell input
# TODO handle invalid json synax
# Note, if a gene is defined twice in input, first one is used, all others are ignored
class CellGeneService(object):
  """Runs REST service that fetches abundance values for cell-gene pair"""

  @route('/context/expression/cell_line', method='POST')
  def test_json():
    """Returns a JSON of abundance values for the provided JSON inputs for CCLE_protein dataset

    Returns:
      A JSON string representing the associated abundance values of cell_line and gene. See JSON format in README
      Returns Null if input is invalid (including integers) or not found in matrix
    """

    # Initialize input dict, CellGene object, output dataframe
    input_set = request.json
    output_df = pd.DataFrame()

    """
    # Make all inputs uppercase
    new_input_set = {}
    for k, v in input_set.iteritems():
      # Make all cell lines uppercase
      new_v = [cell.upper() for cell in v]
      new_input_set[k.upper()] = new_v  
    
    input_set = new_input_set
    """

    # For each gene
    for key, val in input_set.iteritems():

      # Make genes uppercase
      input_set[key.upper()] = input_set[key]
      del input_set[key]
      key = key.upper()
      # Make cell lines uppercase
      input_set[key] = [cell.upper() for cell in val] 

      # Remove duplicate cell lines 
      cell_lines = set(input_set[key])

      # Get abundance for its associated cells and append onto output_df
      abundance_list = cg.get_abundance(key, cell_lines)
      # Skip ducplicate genes
      if key in output_df.index.values:
        break

      output_df = output_df.append(abundance_list)


    output_json = output_df.to_json(orient="index")
    response.content_type = "application/json"
    return output_json

  @route('/context/expression/cell_line/ids_available/<dataset>', method='GET')
  def get_ids(dataset):
    "Returns json of all genes"
    response.content_type = "application/json"
    return cg.get_all_ids()   
  
  @route('/context/expression/cell_line/samples_available/<dataset>', method='GET')
  def get_samples(dataset):
    "Returns json of all cell lines"
    response.content_type = "application/json"
    return cg.get_all_samples()   

  def main():
    """Runs the service on localhost:8080"""
    run(host='localhost', port=8080, debug=True)

  if __name__ == "__main__":
    main()
