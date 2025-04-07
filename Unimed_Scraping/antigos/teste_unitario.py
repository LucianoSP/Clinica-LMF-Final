from todas_as_fases_windows_final import UnimedAutomation
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()


class TestUnimedAutomation(UnimedAutomation):
    def __init__(self):
        super().__init__()
        self.setup_driver()
        self.login(os.getenv("UNIMED_USERNAME"), os.getenv("UNIMED_PASSWORD"))
        time.sleep(2)  # Aguarda o login completar


def test_capture_guides():
    print("\n=== Teste: Captura de Guias ===")
    automation = TestUnimedAutomation()
    try:
        # Teste com período curto e limite de guias
        guides = automation.capture_guides("01/01/2024", "30/01/2024", max_guides=2)
        print("\nGuias capturadas:")
        print(json.dumps(guides, indent=2, ensure_ascii=False))
        return guides
    except Exception as e:
        print(f"\nErro ao capturar guias: {str(e)}")
    finally:
        time.sleep(8)
        automation.driver.quit()


def test_process_single_guide(guide_number="59533336"):
    print(f"\n=== Teste: Processamento da Guia {guide_number} ===")
    automation = TestUnimedAutomation()
    try:
        guide_data = {"numero_guia": guide_number}
        result = automation.process_single_guide(guide_data)
        print("\nResultado do processamento:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"\nErro ao processar guia {guide_number}: {str(e)}")
    finally:
        automation.driver.quit()


def test_search_and_get_guide_dates(guide_number="59533336"):
    print(f"\n=== Teste: Busca de Datas da Guia {guide_number} ===")
    automation = TestUnimedAutomation()
    try:
        if automation.navigate_to_finished_exams():
            dates = automation.search_and_get_guide_dates(guide_number)
            print("\nDatas encontradas:")
            print(json.dumps(dates, indent=2, ensure_ascii=False))
            return dates
    except Exception as e:
        print(f"\nErro ao buscar datas da guia {guide_number}: {str(e)}")
    finally:
        automation.driver.quit()


if __name__ == "__main__":
    # Descomente a função que deseja testar
    test_capture_guides()
    # test_process_single_guide()
    # test_search_and_get_guide_dates()
