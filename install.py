import subprocess as sb
import traceback
import os, sys
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)



def install_requirements():
    print(">>> Installing requirements for this API...")
    script_path = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_path, "requirements.txt")
    print(requirements_path)
    try:
        sb.run(["pip", "install", "-r", requirements_path,"--user"])
    except Exception as e:
        msg = "Problemas al instalar los paquetes necesarios \n" + str(e) +"\n" + traceback.format_exc()
        print(msg)


def prepare_settings():
    print(">>> Prepare settings for this API...")
#    success, msg = Defaults.create_defaults()
#    print(msg)


if __name__ == "__main__":
     install_requirements()
 #   prepare_settings()