import asyncio
import logging
import os
import pathlib
import time
from time import sleep
from typing import Optional

from playwright.async_api import async_playwright, Playwright, Page

logger = logging.getLogger()
SIZE = (1920, 1080)


class BPMNRenderer:
    def __init__(self, headless=True):
        self.headless = headless
        self.__pw: Optional[Playwright] = None
        self.__page: Optional[Page] = None

    async def __init(self):
        if self.__pw is not None: return
        logger.info("Playwright initializing")
        self.__pw = await async_playwright().start()
        self.__target = self.__pw.firefox
        self.__browser = await self.__target.launch(headless=self.headless)
        self.__context = await self.__browser.new_context(viewport=dict(width=SIZE[0], height=SIZE[1]))
        self.__page = await self.__context.new_page()
        base_path = pathlib.Path(__file__).parent.resolve()
        html_path = os.path.join(base_path, "bundling", "public", "index.html")
        await self.__page.goto(f"file://{html_path}")
        logger.info("Playwright ready!")

    async def __export_result(self, timeout=0.3):
        ts = time.time()
        while not (res := await self.__page.evaluate("() => window.result")) and (time.time() - ts) < timeout:
            sleep(0.01)
        img = await self.__page.locator("#canvas").screenshot(type='png')
        pg = await self.__page.evaluate("() => window.xcanvas._cachedViewbox")
        return dict(
            **res,
            png=img,
            scaling=dict(x=pg['x'], y=pg['y'], scale=pg['scale'])
        )

    async def render_by_code(self, exec_script):
        await self.__init()
        logger.info("Rendering BPMN by code models")

        await self.__page.reload()

        await self.__page.evaluate(
            f"() => {{ window.diagramFunction = (makeLink, makeElement) => {{\n{exec_script}\n}} }}"
        )
        await self.__page.evaluate("window.renderByCode()")
        res = await self.__export_result()
        logger.info("Rendering BPMN by code models DONE")
        return res

    async def render_by_xml(self, xml):
        await self.__init()
        logger.info("Rendering BPMN by XML spec")
        await self.__page.evaluate("(xml) => window.renderByXML(xml)", xml)
        res = await self.__export_result()
        logger.info("Rendering BPMN by XML spec DONE")
        return res


def save_all(res):
    with open("test.xml", "w") as f:
        f.write(res['xml'])
    with open("test.svg", "w") as f:
        f.write(res['svg'])
    with open("test.png", "wb") as f:
        f.write(res['png'])


if __name__ == "__main__":
    async def main():
        x = BPMNRenderer()
        res = await x.render_by_code("")
        with open("test.xml", "w") as f:
            f.write(res['xml'])
        with open("test.svg", "w") as f:
            f.write(res['svg'])
        with open("test.png", "wb") as f:
            f.write(res['png'])

        res = await x.render_by_xml("""
        <?xml version="1.0" encoding="UTF-8"?>
    <bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn"><bpmn:process id="Process_0mho0am"><bpmn:task id="process_start_221c3569-b1fb-4188-bd00-c4b97ccc2457" name="SeyROG"><bpmn:outgoing>Flow_1nkuk32</bpmn:outgoing></bpmn:task><bpmn:task id="event_2f784b35-decb-4125-b3ef-f5e5f96ea103" name="ynMxiC"><bpmn:incoming>Flow_1nkuk32</bpmn:incoming><bpmn:outgoing>Flow_0u8uid0</bpmn:outgoing></bpmn:task><bpmn:task id="action_e81fab30-ebba-4632-add0-587bf32ae87a" name="micmdAI"><bpmn:incoming>Flow_0u8uid0</bpmn:incoming><bpmn:outgoing>Flow_1001z8v</bpmn:outgoing></bpmn:task><bpmn:task id="fan_out_43eb836d-79d2-4875-99b4-6c1917f5e1b9" name="SiOWzYnqQa"><bpmn:incoming>Flow_1001z8v</bpmn:incoming><bpmn:outgoing>Flow_1s30nqr</bpmn:outgoing><bpmn:outgoing>Flow_1nwvey8</bpmn:outgoing></bpmn:task><bpmn:task id="event_7ea39004-8850-44b2-a204-c87be1f5a807" name="NSlApduSM"><bpmn:incoming>Flow_1s30nqr</bpmn:incoming><bpmn:outgoing>Flow_0a0fze2</bpmn:outgoing></bpmn:task><bpmn:task id="process_end_d6dd86c6-01e3-4c85-9ece-4d45be2bf654" name="HqIyLL"><bpmn:incoming>Flow_1nwvey8</bpmn:incoming></bpmn:task><bpmn:task id="action_be2f2163-0706-4961-9063-bbd794d2daf8" name="hNYjGSm"><bpmn:incoming>Flow_0a0fze2</bpmn:incoming><bpmn:outgoing>Flow_0t0vctg</bpmn:outgoing></bpmn:task><bpmn:task id="fan_out_3b9125ff-1aa9-4213-ae7f-e58fb0c7e0da" name="SOcFu"><bpmn:incoming>Flow_0t0vctg</bpmn:incoming><bpmn:outgoing>Flow_0am6ijf</bpmn:outgoing><bpmn:outgoing>Flow_09y6k3g</bpmn:outgoing></bpmn:task><bpmn:task id="event_365ea52b-a924-4e93-9ba5-85c34ce11ea2" name="zAudWlJY"><bpmn:incoming>Flow_0am6ijf</bpmn:incoming><bpmn:outgoing>Flow_1mz2bgy</bpmn:outgoing></bpmn:task><bpmn:task id="action_ddad2f8e-b65d-4567-989b-249b9924332b" name="LEmVMKpflH"><bpmn:incoming>Flow_09y6k3g</bpmn:incoming><bpmn:outgoing>Flow_0m0etx7</bpmn:outgoing></bpmn:task><bpmn:task id="fan_out_a6509ebe-7fee-4aad-b317-14707946454c" name="CONhgex"><bpmn:incoming>Flow_1mz2bgy</bpmn:incoming><bpmn:outgoing>Flow_1fs0vt2</bpmn:outgoing></bpmn:task><bpmn:task id="fan_in_a74d5961-8df8-4b5d-a993-64294b19fe72" name="JkKLas"><bpmn:incoming>Flow_0m0etx7</bpmn:incoming><bpmn:incoming>Flow_1fs0vt2</bpmn:incoming><bpmn:outgoing>Flow_1us5wvt</bpmn:outgoing></bpmn:task><bpmn:task id="process_end_172eaf5e-298a-4079-a447-5a48cf6d513b" name="XbcLMXIvn"><bpmn:incoming>Flow_1us5wvt</bpmn:incoming></bpmn:task><bpmn:sequenceFlow id="Flow_1nkuk32" sourceRef="process_start_221c3569-b1fb-4188-bd00-c4b97ccc2457" targetRef="event_2f784b35-decb-4125-b3ef-f5e5f96ea103" /><bpmn:sequenceFlow id="Flow_0u8uid0" sourceRef="event_2f784b35-decb-4125-b3ef-f5e5f96ea103" targetRef="action_e81fab30-ebba-4632-add0-587bf32ae87a" /><bpmn:sequenceFlow id="Flow_1001z8v" sourceRef="action_e81fab30-ebba-4632-add0-587bf32ae87a" targetRef="fan_out_43eb836d-79d2-4875-99b4-6c1917f5e1b9" /><bpmn:sequenceFlow id="Flow_1s30nqr" sourceRef="fan_out_43eb836d-79d2-4875-99b4-6c1917f5e1b9" targetRef="event_7ea39004-8850-44b2-a204-c87be1f5a807" /><bpmn:sequenceFlow id="Flow_1nwvey8" sourceRef="fan_out_43eb836d-79d2-4875-99b4-6c1917f5e1b9" targetRef="process_end_d6dd86c6-01e3-4c85-9ece-4d45be2bf654" /><bpmn:sequenceFlow id="Flow_0a0fze2" sourceRef="event_7ea39004-8850-44b2-a204-c87be1f5a807" targetRef="action_be2f2163-0706-4961-9063-bbd794d2daf8" /><bpmn:sequenceFlow id="Flow_0t0vctg" sourceRef="action_be2f2163-0706-4961-9063-bbd794d2daf8" targetRef="fan_out_3b9125ff-1aa9-4213-ae7f-e58fb0c7e0da" /><bpmn:sequenceFlow id="Flow_0am6ijf" sourceRef="fan_out_3b9125ff-1aa9-4213-ae7f-e58fb0c7e0da" targetRef="event_365ea52b-a924-4e93-9ba5-85c34ce11ea2" /><bpmn:sequenceFlow id="Flow_09y6k3g" sourceRef="fan_out_3b9125ff-1aa9-4213-ae7f-e58fb0c7e0da" targetRef="action_ddad2f8e-b65d-4567-989b-249b9924332b" /><bpmn:sequenceFlow id="Flow_1mz2bgy" sourceRef="event_365ea52b-a924-4e93-9ba5-85c34ce11ea2" targetRef="fan_out_a6509ebe-7fee-4aad-b317-14707946454c" /><bpmn:sequenceFlow id="Flow_0m0etx7" sourceRef="action_ddad2f8e-b65d-4567-989b-249b9924332b" targetRef="fan_in_a74d5961-8df8-4b5d-a993-64294b19fe72" /><bpmn:sequenceFlow id="Flow_1fs0vt2" sourceRef="fan_out_a6509ebe-7fee-4aad-b317-14707946454c" targetRef="fan_in_a74d5961-8df8-4b5d-a993-64294b19fe72" /><bpmn:sequenceFlow id="Flow_1us5wvt" sourceRef="fan_in_a74d5961-8df8-4b5d-a993-64294b19fe72" targetRef="process_end_172eaf5e-298a-4079-a447-5a48cf6d513b" /></bpmn:process><bpmndi:BPMNDiagram id="BPMNDiagram_1"><bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_0mho0am"><bpmndi:BPMNShape id="process_start_221c3569-b1fb-4188-bd00-c4b97ccc2457_di" bpmnElement="process_start_221c3569-b1fb-4188-bd00-c4b97ccc2457"><dc:Bounds x="-50" y="1160" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="event_2f784b35-decb-4125-b3ef-f5e5f96ea103_di" bpmnElement="event_2f784b35-decb-4125-b3ef-f5e5f96ea103"><dc:Bounds x="275" y="1160" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="action_e81fab30-ebba-4632-add0-587bf32ae87a_di" bpmnElement="action_e81fab30-ebba-4632-add0-587bf32ae87a"><dc:Bounds x="600" y="1160" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="fan_out_43eb836d-79d2-4875-99b4-6c1917f5e1b9_di" bpmnElement="fan_out_43eb836d-79d2-4875-99b4-6c1917f5e1b9"><dc:Bounds x="925" y="1160" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="event_7ea39004-8850-44b2-a204-c87be1f5a807_di" bpmnElement="event_7ea39004-8850-44b2-a204-c87be1f5a807"><dc:Bounds x="1250" y="1038.125" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="process_end_d6dd86c6-01e3-4c85-9ece-4d45be2bf654_di" bpmnElement="process_end_d6dd86c6-01e3-4c85-9ece-4d45be2bf654"><dc:Bounds x="1250" y="1281.875" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="action_be2f2163-0706-4961-9063-bbd794d2daf8_di" bpmnElement="action_be2f2163-0706-4961-9063-bbd794d2daf8"><dc:Bounds x="1575" y="1160" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="fan_out_3b9125ff-1aa9-4213-ae7f-e58fb0c7e0da_di" bpmnElement="fan_out_3b9125ff-1aa9-4213-ae7f-e58fb0c7e0da"><dc:Bounds x="1900" y="1160" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="event_365ea52b-a924-4e93-9ba5-85c34ce11ea2_di" bpmnElement="event_365ea52b-a924-4e93-9ba5-85c34ce11ea2"><dc:Bounds x="2225" y="1038.125" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="action_ddad2f8e-b65d-4567-989b-249b9924332b_di" bpmnElement="action_ddad2f8e-b65d-4567-989b-249b9924332b"><dc:Bounds x="2225" y="1281.875" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="fan_out_a6509ebe-7fee-4aad-b317-14707946454c_di" bpmnElement="fan_out_a6509ebe-7fee-4aad-b317-14707946454c"><dc:Bounds x="2550" y="1038.125" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="fan_in_a74d5961-8df8-4b5d-a993-64294b19fe72_di" bpmnElement="fan_in_a74d5961-8df8-4b5d-a993-64294b19fe72"><dc:Bounds x="2550" y="1281.875" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNShape id="process_end_172eaf5e-298a-4079-a447-5a48cf6d513b_di" bpmnElement="process_end_172eaf5e-298a-4079-a447-5a48cf6d513b"><dc:Bounds x="2875" y="1160" width="100" height="80" /></bpmndi:BPMNShape><bpmndi:BPMNEdge id="Flow_1nkuk32_di" bpmnElement="Flow_1nkuk32"><di:waypoint x="50" y="1200" /><di:waypoint x="275" y="1200" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_0u8uid0_di" bpmnElement="Flow_0u8uid0"><di:waypoint x="375" y="1200" /><di:waypoint x="600" y="1200" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_1001z8v_di" bpmnElement="Flow_1001z8v"><di:waypoint x="700" y="1200" /><di:waypoint x="925" y="1200" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_1s30nqr_di" bpmnElement="Flow_1s30nqr"><di:waypoint x="1025" y="1200" /><di:waypoint x="1140" y="1200" /><di:waypoint x="1140" y="1078" /><di:waypoint x="1250" y="1078" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_1nwvey8_di" bpmnElement="Flow_1nwvey8"><di:waypoint x="1025" y="1200" /><di:waypoint x="1140" y="1200" /><di:waypoint x="1140" y="1322" /><di:waypoint x="1250" y="1322" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_0a0fze2_di" bpmnElement="Flow_0a0fze2"><di:waypoint x="1350" y="1078" /><di:waypoint x="1460" y="1078" /><di:waypoint x="1460" y="1200" /><di:waypoint x="1575" y="1200" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_0t0vctg_di" bpmnElement="Flow_0t0vctg"><di:waypoint x="1675" y="1200" /><di:waypoint x="1900" y="1200" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_0am6ijf_di" bpmnElement="Flow_0am6ijf"><di:waypoint x="2000" y="1200" /><di:waypoint x="2110" y="1200" /><di:waypoint x="2110" y="1078" /><di:waypoint x="2225" y="1078" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_09y6k3g_di" bpmnElement="Flow_09y6k3g"><di:waypoint x="2000" y="1200" /><di:waypoint x="2110" y="1200" /><di:waypoint x="2110" y="1322" /><di:waypoint x="2225" y="1322" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_1mz2bgy_di" bpmnElement="Flow_1mz2bgy"><di:waypoint x="2325" y="1078" /><di:waypoint x="2550" y="1078" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_0m0etx7_di" bpmnElement="Flow_0m0etx7"><di:waypoint x="2325" y="1322" /><di:waypoint x="2550" y="1322" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_1fs0vt2_di" bpmnElement="Flow_1fs0vt2"><di:waypoint x="2600" y="1118" /><di:waypoint x="2600" y="1282" /></bpmndi:BPMNEdge><bpmndi:BPMNEdge id="Flow_1us5wvt_di" bpmnElement="Flow_1us5wvt"><di:waypoint x="2650" y="1322" /><di:waypoint x="2760" y="1322" /><di:waypoint x="2760" y="1200" /><di:waypoint x="2875" y="1200" /></bpmndi:BPMNEdge></bpmndi:BPMNPlane></bpmndi:BPMNDiagram></bpmn:definitions>
        """)
        with open("test.xml", "w") as f:
            f.write(res['xml'])
        with open("test.svg", "w") as f:
            f.write(res['svg'])
        with open("test.png", "wb") as f:
            f.write(res['png'])


    asyncio.run(main())
