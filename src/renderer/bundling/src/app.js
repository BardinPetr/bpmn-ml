// noinspection ES6UnusedImports

import 'bpmn-js/dist/assets/diagram-js.css';
import 'bpmn-js/dist/assets/bpmn-js.css';
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css';
import BpmnModeler from 'bpmn-js/lib/Modeler';
import Modeling from 'bpmn-js/lib/features/modeling/Modeling';
import BpmnFactory from 'bpmn-js/lib/features/modeling/BpmnFactory';
import ElementFactory from 'bpmn-js/lib/features/modeling/ElementFactory';
import ElementRegistry from 'diagram-js/lib/core/ElementRegistry';

const container = document.querySelector('.modeler');
const modeler = new BpmnModeler({
    container
});

async function diagexport() {
    const {svg} = await modeler.saveSVG();
    const {xml} = await modeler.saveXML()
    window.result = {svg, xml}
    window.xcanvas = modeler.get('canvas')
    window.xcanvas.zoom('fit-viewport')
}

async function run(code) {
    const diagram = await modeler.createDiagram()
    // await modeler.clear()

    const bpmnFactory = /** @type {BpmnFactory} */ modeler.get('bpmnFactory'),
        elementFactory = /** @type {ElementFactory} */ modeler.get('elementFactory'),
        elementRegistry = /** @type {ElementRegistry} */ modeler.get('elementRegistry'),
        modeling =/** @type {Modeling} */ modeler.get('modeling'),
        eventBus =/** @type {EventBus} */ modeler.get('eventBus');

    window.bpmnFactory = bpmnFactory;
    window.elementFactory = elementFactory;
    window.elementRegistry = elementRegistry;
    window.modeling = modeling;
    window.modeler = modeler;

    const process = modeling.makeProcess()
    const processes = {
        "0": process
    }

    function makeElement(uid, name, bpmn_type, bpmn_add_def, px, py, process_id) {
        const t1 = bpmnFactory.create(bpmn_type, {id: uid, name});

        let data = {
            type: bpmn_type,
            businessObject: t1
        };
        if (bpmn_add_def.length > 0) {
            data.eventDefinitionType = bpmn_add_def
        }

        const t1s = elementFactory.createShape(data);

        modeling.createShape(t1s, {x: px, y: py}, processes[process_id]);
    }

    function makeLink(uid1, uid2, label) {
        const conn = modeling.connect(
            elementRegistry.get(uid1),
            elementRegistry.get(uid2),
            {type: 'bpmn:SequenceFlow'}
        )
        modeling.updateLabel(conn, label)
    }

    window.diagramFunction(makeLink, makeElement)
    await diagexport();
}

async function runxml(code) {
    await modeler.importXML(code)
    await diagexport();
}

window.result = null
window.renderByCode = () => run().then()
window.renderByXML = (code) => runxml(code).then()
