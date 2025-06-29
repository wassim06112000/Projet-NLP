import os
import json
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List

# Namespaces
NS = {
    'jo': 'http://boamp.journal-officiel.gouv.fr/XML/3.2.5',
    'cbc': 'urn:boamp:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:boamp:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
    'ext': 'urn:boamp:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
}

def safe_find(element, xpath: str) -> Optional[ET.Element]:
    """Safely find an element with error handling"""
    try:
        return element.find(xpath, NS)
    except Exception:
        return None

def get_text(element: Optional[ET.Element], xpath: str, default: Optional[str] = None) -> Optional[str]:
    """Safely get text from an element"""
    if element is None:
        return default
    target = safe_find(element, xpath)
    return target.text.strip() if target is not None and target.text else default

def get_attribute(element: Optional[ET.Element], xpath: str, attr: str, default: Optional[str] = None) -> Optional[str]:
    """Safely get an attribute from an element"""
    target = safe_find(element, xpath)
    return target.get(attr, default) if target is not None else default

def parse_contracting_party(root: ET.Element) -> Dict[str, Any]:
    """Extract contracting party information"""
    party = safe_find(root, './/cac:ContractingParty')
    if party is None:
        return {}
    
    return {
        'name': get_text(party, './/cac:PartyName/cbc:Name'),
        'legal_type': get_text(party, './/cbc:PartyTypeCode'),
        'activity': get_text(party, './/cbc:ActivityTypeCode'),
        'address': {
            'street': get_text(party, './/cbc:StreetName'),
            'city': get_text(party, './/cbc:CityName'),
            'postal_code': get_text(party, './/cbc:PostalZone'),
            'country': get_text(party, './/cac:Country/cbc:IdentificationCode')
        },
        'contact': {
            'phone': get_text(party, './/cbc:Telephone'),
            'email': get_text(party, './/cbc:ElectronicMail')
        }
    }

def parse_procurement_project(root: ET.Element) -> Dict[str, Any]:
    """Extract main project information"""
    project = safe_find(root, './/cac:ProcurementProject')
    if project is None:
        return {}
    
    return {
        'title': get_text(project, './cbc:Name'),
        'description': get_text(project, './cbc:Description'),
        'type': get_text(project, './cbc:ProcurementTypeCode'),
        'cpv_codes': [get_text(e, '.') 
                     for e in project.findall('.//cac:MainCommodityClassification/cbc:ItemClassificationCode', NS)],
        'estimated_value': get_text(root, './/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount'),
        'currency': get_attribute(root, './/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount', 'currencyID')
    }

def parse_tendering_process(root: ET.Element) -> Dict[str, Any]:
    """Extract tendering process information"""
    process = safe_find(root, './/cac:TenderingProcess')
    if process is None:
        return {}
    
    return {
        'description': get_text(process, './cbc:Description'),
        'procedure_type': get_text(process, './cbc:ProcedureCode'),
        'notice_reference': get_text(process, './cac:NoticeDocumentReference/cbc:ID')
    }

def parse_lot(lot: ET.Element) -> Dict[str, Any]:
    """Parse individual lot information"""
    project = safe_find(lot, './cac:ProcurementProject')
    tender_total = safe_find(lot, './/cac:RequestedTenderTotal')
    
    return {
        'id': get_text(lot, './cbc:ID'),
        'title': get_text(project, './cbc:Name'),
        'description': get_text(project, './cbc:Description'),
        'estimated_value': get_text(tender_total, './cbc:EstimatedOverallContractAmount'),
        'currency': get_attribute(tender_total, './cbc:EstimatedOverallContractAmount', 'currencyID'),
        'cpv_code': get_text(lot, './/cac:MainCommodityClassification/cbc:ItemClassificationCode'),
        'location': {
            'description': get_text(lot, './/cac:RealizedLocation/cbc:Description'),
            'city': get_text(lot, './/cac:Address/cbc:CityName'),
            'country': get_text(lot, './/cac:Country/cbc:IdentificationCode')
        },
        'award_criteria': [
            {
                'type': get_text(crit, './/cbc:AwardingCriterionTypeCode'),
                'description': get_text(crit, './/cbc:Description'),
                'weight': get_text(crit, './/efac:AwardCriterionParameter/efbc:ParameterNumeric')
            }
            for crit in lot.findall('.//cac:AwardingCriterion', NS)
        ]
    }

def parse_xml_file(xml_path: str) -> Optional[Dict[str, Any]]:
    """Parse a single XML file with robust error handling"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        if root is None:
            print(f"Fichier {xml_path} a un root None")
            return None

        # Extract all key elements
        data = {
            'filename': os.path.basename(xml_path),
            'project': parse_procurement_project(root),
            'tendering_process': parse_tendering_process(root),
            'lots': [parse_lot(lot) for lot in root.findall('.//cac:ProcurementProjectLot', NS)]
        }
        idx = safe_find(root, './/jo:INDEXATION')
        if idx is not None:
            data['titre']             = get_text(idx, 'gest:TITRE')            or get_text(idx, 'TITRE')
            data['resume_detaille']   = get_text(idx, 'gest:RESUME_OBJET')      or get_text(idx, 'RESUME_OBJET')
            data['acheteur']          = get_text(idx, 'gest:NOMORGANISME')      or get_text(idx, 'NOMORGANISME')
            data['date_publication']  = get_text(idx, 'gest:DATE_PUBLICATION')  or get_text(idx, 'DATE_PUBLICATION')
            data['date_fin_diffusion']= get_text(idx, 'gest:DATE_FIN_DIFFUSION')or get_text(idx, 'DATE_FIN_DIFFUSION')
            data['departement']       = get_text(idx, 'gest:DEP_PUBLICATION')   or get_text(idx, 'DEP_PUBLICATION')
            # et si besoin les descripteurs :
            descrs = []
            for d in idx.findall('gest:DESCRIPTEURS/gest:DESCRIPTEUR', NS) + idx.findall('DESCRIPTEURS/DESCRIPTEUR'):
                lib = get_text(d, 'gest:LIBELLE') or get_text(d, 'LIBELLE')
                if lib:
                    descrs.append(lib)
            data['descripteurs'] = descrs

        return data

    except ET.ParseError as e:
        print(f"Erreur XML dans {xml_path}: {str(e)}")
        return None
    except Exception as e:
        print(f"Erreur inattendue avec {xml_path}: {str(e)}")
        return None

def process_xml_files(input_dir: str, output_file: str) -> None:
    """Process all XML files in directory"""
    if not os.path.exists(input_dir):
        print(f"Le dossier {input_dir} n'existe pas")
        return

    results = []
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.xml'):
            filepath = os.path.join(input_dir, filename)
            print(f"Traitement de {filename}...")
            
            result = parse_xml_file(filepath)
            if result:
                results.append(result)
            else:
                print(f"Échec du traitement pour {filename}")

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Résultats sauvegardés dans {output_file} ({len(results)} fichiers traités)")

