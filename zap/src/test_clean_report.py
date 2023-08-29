from urllib.parse import urlparse, urlunparse
import defusedxml.ElementTree as ET
import re
import os

def clean_uri_path(xml_report):
    """
    Remove the changing hash from the path of static resources in zap report.
    """

    tree = ET.parse(xml_report)
    root = tree.getroot()
    #There's a hash in bundled files that is causing flaws to not match, this should remove the hash.
    for uri in root.iter('uri'):
        r = urlparse(uri.text)
        r = r._replace(path=re.sub('[-\.][a-fA-F0-9]{8,9}[^a-fA-F0-9]', '', r.path))
        uri.text = urlunparse(r)
    tree.write(xml_report)

def test_regex(xml_report):

    xml_report_ref = xml_report + ".ref"
    xml_report_mod = xml_report + ".mod"

    # rewrite a file with no replacements so formatting changes don't confuse diff
    tree = ET.parse(xml_report)
    root = tree.getroot()
    for uri in root.iter('uri'):
        r = urlparse(uri.text)
        uri.text = urlunparse(r)
    tree.write(xml_report_ref)

    # copy the reference file
    tree = ET.parse(xml_report)
    root = tree.getroot()
    #There's a hash in bundled files that is causing flaws to not match, this should remove the hash.
    for uri in root.iter('uri'):
        r = urlparse(uri.text)
        old_regex = '\.([a-zA-Z0-9]+){8,9}'
        new_regex = '[-\.][a-fA-F0-9]{8,9}(?![a-fA-F0-9])'
        r = r._replace(path=re.sub(new_regex, '', r.path))
        uri.text = urlunparse(r)
    tree.write(xml_report_mod)
    # os.system(f"diff {xml_report_ref} {xml_report_mod}")


if __name__ == "__main__":
    # report_tobe_cleaned = input("path to copy of report to be cleaned. ")
    # clean_uri_path(report_tobe_cleaned)
    test_regex("manual.xml")