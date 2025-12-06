from enum import Enum
import os

def load_from_file(window):
    config_file = "config.txt"

    if not os.path.exists(config_file):
        print("Ustawienia domyślne")
        return
    
    try:
        file = open(config_file, "r", encoding="utf-8")
        lines = file.readlines()
        file.close()
       

        
        settings = []
        for line in lines:
            settings.append(line.strip())

        
        if len(settings) < len(conf_sett):
            print("plik konfiguracyjny jest uszkodzony")
            return
            
        window.saved_sd_url = settings[conf_sett.url.value]

        try:
            tool_id = int(settings[conf_sett.tool.value])
            tool_indx = window.tool_combo.findData(tool_id)
            if tool_indx in [0,1]:
                window.tool_combo.setCurrentIndex(tool_indx)
        except ValueError:
            pass

        try:
            method_id = int(settings[conf_sett.inpaint_method.value])
            method_idx = window.fill_combo.findData(method_id)
            if method_idx in [0,1,2,3,4]:
                window.fill_combo.setCurrentIndex(method_idx)
        except ValueError:
            pass


        window.saved_prompt = settings[conf_sett.prompt.value]
        

        window.saved_negative_prompt = settings[conf_sett.negative_prompt.value]

        try:
            window.saved_steps = int(settings[conf_sett.steps.value])
        except ValueError:
            window.saved_steps = 25

        try:
            window.saved_denoising = float(settings[conf_sett.denoising.value])
        except ValueError:
            window.saved_denoising = 0.7

        try:
            window.saved_cfg_scale = float(settings[conf_sett.cfg_scale.value])
        except ValueError:
            window.saved_cfg_scale = 7.0


    except Exception as e:
        print(f"Błąd podczas wczytywania pliku: {e}")
                
            

def save_config(window):
    config_file = "config.txt"
    url = getattr(window, 'saved_sd_url', "Brak URL")

    
    dzejson = ""

    #first)lauch
    dzejson += "0" + "\n"

    #url
    dzejson += url + "\n"

    #tool
    tool_combo = getattr(window, 'tool_combo', None)
    tool_id = tool_combo.currentData()
    dzejson += str(tool_id) + "\n"

    #fill
    fill_combo = getattr(window, 'fill_combo', None)
    fill_id = fill_combo.currentData()
    dzejson += str(fill_id) + "\n"

    prompt = getattr(window, 'saved_prompt')
    dzejson += str(prompt) + "\n"
    
    negative_prompt = getattr(window, 'saved_negative_prompt')
    dzejson += str(negative_prompt) + "\n"
    
    steps = getattr(window, 'saved_steps')
    dzejson += str(steps) + "\n"
    
    denoising = getattr(window, 'saved_denoising')
    dzejson += str(denoising) + "\n"
    
    cfg_scale = getattr(window, 'saved_cfg_scale')
    dzejson += str(cfg_scale) + "\n"
    
    
    print(dzejson)
    save = open(config_file,"w")
    save.write(dzejson)

    save.close()


class conf_sett(Enum):
    first_lauch = 0
    url = 1
    tool = 2
    inpaint_method = 3
    prompt = 4
    negative_prompt = 5
    steps = 6
    denoising = 7
    cfg_scale = 8
    

