import xml.etree.ElementTree as ET
import argparse
parser = argparse.ArgumentParser(description='Codedx project')
parser.add_argument('project', type=str, help='The project')
parser.add_argument('url', type=str, help='The "joint project" url')
parser.add_argument('host', type=str, help='The "joint project" host')
parser.add_argument('input', type=str, help='The input xml file')
parser.add_argument('output', type=str, help='The output xml file')
args = parser.parse_args()

output_file = args.output
f = open(output_file, "a")

tree = ET.parse(args.input)
if tree.getroot().tag == 'OWASPZAPReport':
	tree.getroot()[0].set('name', args.url)
	tree.getroot()[0].set('host', args.host)
	tree.getroot()[0].attrib
	for alert in tree.getroot()[0][0].iter('alertitem'):
		for uri in alert.iter('uri'):
			uri_loc = uri.text.split('/')
			if len(uri_loc) < 4:
				uri_loc.append(args.project + '/')
			else:
				uri_loc[3] = args.project + '/' + uri_loc[3]
			uri_loc[2] = 'www.' + args.host
			new_uri = '/'.join(uri_loc)
			uri.text = new_uri
		f.write(ET.tostring(alert))
else:
	for issue in tree.getroot():
		path = issue.find('path')
		path.text = '/' + args.project + path.text

f.close()