# openpoiservice/server/parser.py

from openpoiservice.server.db_import.parse_osm import OsmImporter
from openpoiservice.server.utils.decorators import timeit, processify
from openpoiservice.server import ops_settings
from openpoiservice.server import logger
from imposm.parser import OSMParser

# from guppy import hpy
from collections import deque

# h = hpy()
log = logger.get_logger(__name__)


# process this function to free memory after import of each osm file

def parse_import(osm_file):
    log.info('Starting to read {}'.format(osm_file))

    osm_importer = OsmImporter()

    log.info('Parsing and importing nodes...')
    nodes = OSMParser(concurrency=ops_settings['concurrent_workers'], nodes_callback=osm_importer.parse_nodes)
    nodes.parse(osm_file)

    log.info('Parsing relations...')
    relations = OSMParser(concurrency=ops_settings['concurrent_workers'],
                          relations_callback=osm_importer.parse_relations)
    relations.parse(osm_file)
    log.info('Found {} ways in relations'.format(osm_importer.relations_cnt))

    log.info('Parsing ways...')
    ways = OSMParser(concurrency=ops_settings['concurrent_workers'], ways_callback=osm_importer.parse_ways)
    ways.parse(osm_file)

    log.info('Found {} ways'.format(osm_importer.ways_cnt))
    del osm_importer.relation_ways

    # Sort the ways by the first osm_id reference, saves memory for parsing coords
    osm_importer.process_ways.sort(key=lambda x: x.refs[0])
    # init self.process_ways_length before the first call of parse_coords function!
    osm_importer.process_ways_length = len(osm_importer.process_ways)

    # https://docs.python.org/3/library/collections.html#collections.deque
    osm_importer.process_ways = deque(osm_importer.process_ways)
    log.info('Importing ways... (note this wont work concurrently)')

    coords = OSMParser(concurrency=1, coords_callback=osm_importer.parse_coords_for_ways)
    coords.parse(osm_file)

    log.info('Storing remaining pois')
    osm_importer.save_remainder()

    log.info('Found {} pois'.format(osm_importer.pois_cnt))

    log.info('Finished import of {}'.format(osm_file))

    # log.debug('Heap: {}'.format(h.heap()))

    # clear memory
    del osm_importer


@processify
def parse_file(osm_file):
    parse_import(osm_file)


@timeit
def run_import(osm_files_to_import):

    for osm_file in osm_files_to_import:

        parse_file(osm_file)
