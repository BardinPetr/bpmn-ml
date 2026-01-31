import xml.etree.ElementTree as ET
from typing import Optional

from bpmn_models import BPMNFlow, BPMNDiagram, BPMNElement, BPMNProcess


class BPMNParser:
    """Parser for BPMN 2.0 XML files"""

    # BPMN 2.0 namespace
    BPMN_NS = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
    BPMNDI_NS = '{http://www.omg.org/spec/BPMN/20100524/DI}'
    DI_NS = '{http://www.omg.org/spec/DD/20100524/DI}'
    DC_NS = '{http://www.omg.org/spec/DD/20100524/DC}'

    # Element type mappings
    ELEMENT_TYPES = {
        'task': ['task', 'userTask', 'serviceTask', 'sendTask',
                 'receiveTask', 'manualTask', 'businessRuleTask', 'scriptTask'],
        'gateway': ['exclusiveGateway', 'parallelGateway', 'inclusiveGateway',
                    'eventBasedGateway', 'complexGateway'],
        'event': ['startEvent', 'endEvent', 'intermediateThrowEvent',
                  'intermediateCatchEvent', 'boundaryEvent'],
        'subProcess': ['subProcess', 'transaction', 'adHocSubProcess'],
        'data': ['dataObjectReference', 'dataStoreReference'],
        'artifact': ['textAnnotation', 'group']
    }

    @classmethod
    def _register_namespaces(cls, root):
        """Extract and register namespaces from root"""
        ns = {}
        for attr_name, attr_value in root.attrib.items():
            if attr_name.startswith('xmlns:'):
                prefix = attr_name.split(':')[1]
                ns[prefix] = attr_value
            elif attr_name == 'xmlns':
                ns[''] = attr_value

        # Register all namespaces
        for prefix, uri in ns.items():
            if prefix:
                print(prefix, uri)
                ET.register_namespace(prefix, uri)

    @classmethod
    def _get_tag_name(cls, element):
        """Extract tag name without namespace"""
        tag = element.tag
        # Remove namespace
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag

    @classmethod
    def _get_element_type_and_subtype(cls, tag_name):
        """Determine element type and subtype from tag name"""
        for elem_type, subtypes in cls.ELEMENT_TYPES.items():
            if tag_name in subtypes:
                return elem_type, tag_name

        # Default mapping
        if tag_name in ['laneSet', 'lane', 'participant']:
            return 'container', tag_name
        elif tag_name == 'collaboration':
            return 'collaboration', tag_name

        return 'other', tag_name

    @classmethod
    def _parse_bounds(cls, bounds_element):
        """Parse bounds element to tuple (x, y, width, height)"""
        if bounds_element is None:
            return None

        x = float(bounds_element.get('x', 0))
        y = float(bounds_element.get('y', 0))
        width = float(bounds_element.get('width', 0))
        height = float(bounds_element.get('height', 0))

        return (x, y, width, height)

    @classmethod
    def _parse_waypoints(cls, edge_element):
        """Parse waypoints from edge element"""
        waypoints = edge_element.findall(f'.//{cls.DI_NS}waypoint')
        if len(waypoints) >= 2:
            first = waypoints[0]
            last = waypoints[-1]
            x0 = float(first.get('x', 0))
            y0 = float(first.get('y', 0))
            x1 = float(last.get('x', 0))
            y1 = float(last.get('y', 0))
            return (x0, y0, x1, y1)
        return None

    @classmethod
    def _parse_expression(cls, flow_element):
        """Parse condition expression from flow element"""
        condition = flow_element.find(f'{cls.BPMN_NS}conditionExpression')
        if condition is not None:
            # Try to get text content
            if condition.text and condition.text.strip():
                return condition.text.strip()
            # Try to get xsi:type attribute for formal expressions
            expr_type = condition.get('{http://www.w3.org/2001/XMLSchema-instance}type', '')
            if 'tFormalExpression' in expr_type:
                return condition.get('{http://www.w3.org/1999/xhtml}body', '')
        return None

    @classmethod
    def _parse_process_elements(cls, process_element, shapes_map):
        """Parse all elements within a process"""
        elements = []

        # Find all flow elements (sequence flows first for reference)
        for elem in process_element:
            tag_name = cls._get_tag_name(elem)

            # Skip non-element tags
            if tag_name in ['sequenceFlow', 'messageFlow', 'documentation',
                            'extensionElements', 'laneSet']:
                continue

            # Create BPMNElement
            element_id = elem.get('id', '')
            if not element_id:
                continue

            element_type, subtype = cls._get_element_type_and_subtype(tag_name)

            bpmn_element = BPMNElement(
                id=element_id,
                name=elem.get('name'),
                type=element_type,
                subtype=subtype,
                incoming=[],
                outgoing=[],
                bbox=shapes_map.get(element_id)
            )

            elements.append(bpmn_element)

        return elements

    @classmethod
    def _parse_flows(cls, process_element, edges_map, flow_type='sequence'):
        """Parse flows within a process"""
        flows = []

        flow_tag = 'sequenceFlow' if flow_type == 'sequence' else 'messageFlow'

        for flow_elem in process_element.findall(f'{cls.BPMN_NS}{flow_tag}'):
            flow_id = flow_elem.get('id', '')
            if not flow_id:
                continue

            flow = BPMNFlow(
                id=flow_id,
                source_ref=flow_elem.get('sourceRef', ''),
                target_ref=flow_elem.get('targetRef', ''),
                type=flow_type,
                name=flow_elem.get('name'),
                expression=cls._parse_expression(flow_elem),
                line=edges_map.get(flow_id)
            )
            flows.append(flow)

        return flows

    @classmethod
    def _link_elements_and_flows(cls, elements, flows):
        """Link elements with their incoming/outgoing flows"""
        # Create element lookup
        element_map = {elem.id: elem for elem in elements}

        # Update incoming/outgoing references
        for flow in flows:
            source_elem = element_map.get(flow.source_ref)
            target_elem = element_map.get(flow.target_ref)

            if source_elem:
                source_elem.outgoing.append(flow.id)

            if target_elem:
                target_elem.incoming.append(flow.id)

    @classmethod
    def _parse_diagram_info(cls, root):
        """Parse diagram information (shapes and edges)"""
        shapes_map = {}
        edges_map = {}

        # Find BPMNDiagram element
        diagram = root.find(f'.//{cls.BPMNDI_NS}BPMNDiagram')
        if diagram is None:
            return shapes_map, edges_map

        # Find BPMNPlane
        plane = diagram.find(f'{cls.BPMNDI_NS}BPMNPlane')
        if plane is None:
            return shapes_map, edges_map

        # Parse shapes
        for shape in plane.findall(f'{cls.BPMNDI_NS}BPMNShape'):
            bpmn_element = shape.get('bpmnElement')
            if bpmn_element:
                bounds = shape.find(f'{cls.DC_NS}Bounds')
                shapes_map[bpmn_element] = cls._parse_bounds(bounds)

        # Parse edges
        for edge in plane.findall(f'{cls.BPMNDI_NS}BPMNEdge'):
            bpmn_element = edge.get('bpmnElement')
            if bpmn_element:
                edges_map[bpmn_element] = cls._parse_waypoints(edge)

        return shapes_map, edges_map

    @classmethod
    def _parse_collaboration(cls, root, shapes_map, edges_map):
        """Parse collaboration diagram with participants and message flows"""
        collaboration = root.find(f'{cls.BPMN_NS}collaboration')
        if collaboration is None:
            return {}, []

        # Parse participants (lanes/pools)
        participants = {}
        for participant in collaboration.findall(f'{cls.BPMN_NS}participant'):
            participant_id = participant.get('id', '')
            process_ref = participant.get('processRef', '')
            name = participant.get('name', '')

            if participant_id and process_ref:
                participants[process_ref] = name

        # Parse message flows (inter-process flows)
        interprocess_flows = []
        for msg_flow in collaboration.findall(f'{cls.BPMN_NS}messageFlow'):
            flow_id = msg_flow.get('id', '')
            if not flow_id:
                continue

            flow = BPMNFlow(
                id=flow_id,
                source_ref=msg_flow.get('sourceRef', ''),
                target_ref=msg_flow.get('targetRef', ''),
                type='message',
                name=msg_flow.get('name'),
                line=edges_map.get(flow_id)
            )
            interprocess_flows.append(flow)

        return participants, interprocess_flows

    @classmethod
    def load_xml(cls, xml_text: str):
        root = ET.fromstring(xml_text)
        cls._register_namespaces(root)
        return ET, root

    @classmethod
    def parse_bpmn(cls, xml_text: str) -> Optional[BPMNDiagram]:
        """
        Parse BPMN XML text into BPMNDiagram object

        Args:
            xml_text: BPMN 2.0 XML string

        Returns:
            BPMNDiagram object or None if parsing fails
        """
        try:
            # Parse XML
            root = ET.fromstring(xml_text)

            # Register namespaces
            cls._register_namespaces(root)

            # Parse diagram information (shapes and edges)
            shapes_map, edges_map = cls._parse_diagram_info(root)

            # Parse collaboration if exists
            participants, interprocess_flows = cls._parse_collaboration(
                root, shapes_map, edges_map
            )

            # Parse all processes
            processes = []
            for process_elem in root.findall(f'{cls.BPMN_NS}process'):
                process_id = process_elem.get('id', '')
                if not process_id:
                    continue

                # Get participant name if exists
                participant_name = participants.get(process_id)

                # Parse process elements
                elements = cls._parse_process_elements(process_elem, shapes_map)

                # Parse sequence flows
                flows = cls._parse_flows(process_elem, edges_map, 'sequence')

                # Link elements with flows
                cls._link_elements_and_flows(elements, flows)

                # Create BPMNProcess
                process = BPMNProcess(
                    id=process_id,
                    name=process_elem.get('name', f'Process_{process_id}'),
                    participant_name=participant_name,
                    elements=elements,
                    flows=flows
                )

                processes.append(process)

            # If no processes found, check for single process in root
            if not processes:
                # Try to find process directly
                process_elem = root.find(f'{cls.BPMN_NS}process')
                if process_elem is not None:
                    process_id = process_elem.get('id', '')
                    elements = cls._parse_process_elements(process_elem, shapes_map)
                    flows = cls._parse_flows(process_elem, edges_map, 'sequence')
                    cls._link_elements_and_flows(elements, flows)

                    process = BPMNProcess(
                        id=process_id,
                        name=process_elem.get('name', f'Process_{process_id}'),
                        elements=elements,
                        flows=flows
                    )
                    processes.append(process)

            # Create and return diagram
            return BPMNDiagram(
                processes=processes,
                interprocess_flows=interprocess_flows
            )

        except Exception as e:
            print(f"Error parsing BPMN XML: {e}")
            import traceback
            traceback.print_exc()
            return None


def parse_bpmn(xml_text: str) -> Optional[BPMNDiagram]:
    r = BPMNParser.parse_bpmn(xml_text)
    return r
