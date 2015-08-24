""" fgdc.py

    Processing functions for processing FGDC

    Spec: http://www.fgdc.gov/metadata/csdgm/00.html
    Relevant Section: http://www.fgdc.gov/metadata/csdgm/10.html

    People and organization information comes in two locations in the document.

    Location 1: /metadata/metainfo/metc
    This is the "metadata contact"

    <metadata>
        ...
        <metainfo>
            <metd>20120328</metd>
            <metrd/>
            <metfrd/>
            <metc>
              <cntinfo>
                <cntorgp>
                  <cntorg>Information Center for the Environment...</cntorg>
                  <cntper>Rob Coman</cntper>
                </cntorgp>
                <cntpos/>
                <cntaddr>
                  <addrtype>mailing</addrtype>
                  <address>University of California, Davis</address>
                  <address>One Shields Avenue</address>
                  <city>Davis</city>
                  <state>CA</state>
                  <postal>95616</postal>
                  <country>USA</country>
                </cntaddr>
                <cntvoice/>
                <cntemail/>
              </cntinfo>
            </metc>
            <metstdn>
                FGDC Content Standard for Digital Geospatial Metadata
            </metstdn>
            <metstdv>FGDC-STD-001-1998</metstdv>
            </metainfo>
        </metadata>

    Location 2: /metadata/ptcontac
    This seems to be the contact for the data itself.

    <metadata>
        ...
        <ptcontac>
            <cntinfo>
                <cntorgp>
                    <cntorg>California Department of P...</cntorg>
                    <cntper>Leah Godsey Walker, P.E. - Chief, D...</cntper>
                </cntorgp>
                <cntaddr>
                    <addrtype>mailing</addrtype>
                    <address>1615 Capitol Avenue</address>
                    <city>Sacramento</city>
                    <state>CA</state>
                    <postal>95815-5015</postal>
                    <country>USA</country>
                </cntaddr>
                <cntvoice/>
                <cntemail/>
            </cntinfo>
        </ptcontac>
    </metadata>

    Fields to extract:

    metadata/metainfo/metc  <cntinfo> cntorg + cntper + cntaddr +
                                                cntemail + cntvoice

    metadata/ptcontac       <cntinfo/cntperp> + cntper + cntaddr +
                                                cntvoice + cntemail
        For when the person is more important than the organization

    metadata/ptcontac       <cntinfo/cntorgp> + cntper + cntaddr +
                                                cntvoice + cntemail
        For when the organization is more important than the person
"""


def process(job, xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    # TODO: Process ptcontac
    # TODO: Process others? org?

    info = xmldoc.find("./metainfo/metc/cntinfo")

    if info is not None:
        processContactInfo(job, info, document)


def processContactInfo(job, info, document):
    # Blank record
    record = {}

    # Branch here depending on whether we have cntorgp and/or cntperp
    # If it's a cntorgp, we save it as an organization
    # If it's a cntperp, we save it as a person

    cntperp = info.find("./cntperp")
    cntorgp = info.find("./cntorgp")

    if cntperp is not None:
        name = cntperp.find("./cntper")
        org = cntperp.find("./cntorg")

        if name is not None:
            record['name'] = name.text

        if org is not None:
            record['org'] = org.text

    if cntorgp is not None:
        org = cntorgp.find("./cntorg")

        if org is not None:
            record['org'] = org.text

    address = info.find("./cntaddr")
    email = info.find("./cntemail")
    voice = info.find("./cntvoice")

    if address is not None:
        processAddress(record, address)

    if email is not None and email.text is not None:
        record['email'] = email.text

    if voice is not None and voice.text is not None:
        record['phone'] = voice.text

    record['document'] = document
    record['format'] = "FGDC"

    if cntperp is not None:
        job.people.append(record)

    if cntorgp is not None:
        job.organizations.append(record)


def processAddress(record, address):
    address_nodes = address.findall("./address")
    city = address.find("./city")
    state = address.find("./state")
    postal = address.find("./postal")
    country = address.find("./country")

    fields = []

    if address_nodes is not None:
        for node in address_nodes:
            fields.append(node.text)

    if city is not None:
        fields.append(city.text)

    if state is not None:
        fields.append(state.text)

    if postal is not None:
        fields.append(postal.text)

    if country is not None:
        fields.append(country.text)

    if len(fields) > 0:
        record['address'] = " ".join([f for f in fields if f is not None])

    return record
