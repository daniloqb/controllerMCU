#!flask/bin/python
from Devices import *
from flask import Flask,jsonify, make_response, abort, request



nec = DatashowNEC()
york = AirConditioner()


controllerCOM = ControllerCOMDeviceJson('/dev/ttyUSB0',9600)


app = Flask(__name__)



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error':'not found'}),404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error':'bad request'}),400)


'''
This part of code is responsible for the status
'''

@app.route('/controllerMCU/status',methods=['GET'])
def control_status():
    d = dict()
    d['state'] = 'all'
    status = controllerCOM.execute(d);
    return jsonify(json.loads(status))



'''
This part of code is reponsible for the datashow controller

'''

@app.route('/controllerMCU/datashow',methods=['POST'])
def control_datashow():

    if not request.json or not 'action' in request.json:
        abort(400)

    action = request.json['action']

    if action == 'powerOn':
        nec.powerOn()
    elif action == 'powerOff':
        nec.powerOff()
    else:
        return jsonify({'error':'unknown function'})

    controllerCOM.execute(nec.getJsonCode());
    return jsonify(nec.getJsonCode())


'''

This part of code is responsible for air conditioneer control

'''

@app.route('/controllerMCU/airconditioneer',methods=['POST'])
def control_airconditioneer():

    valid_commands = False

    if not request.json:
        abort(400)


    #verify the action parameter

    if 'act' in request.json:
        act = request.json['act']
        if act in ['normal','clear','filter','sleep','offtimer','ontimer']:
            valid_commands = True
            york.setAct(act)
        else:
            return jsonify({'error':'invalid action'})


    #verify the status parameter

    if 'status' in request.json:
        status = request.json['status']
        if status in ['on', 'off']:
            valid_commands = True
            york.setStatus(status)
        else:
            return jsonify({'error':'invalid status'})


    #verify the mode parameter

    if 'mode' in request.json:
        mode = request.json['mode']
        if mode in ['fan','cool','dry']:
            valid_commands = True
            york.setMode(mode)
        else:
            return jsonify({'error': 'invalid mode'})


    #verify the fan parameter

    if 'fan' in request.json:
        fan = request.json['fan']
        if fan in ['01','02','03','auto']:
            valid_commands = True
            york.setFan(fan)
        else:
            return jsonify({'error': 'invalid fan'})


    #verify the sweep parameter

    if 'sweep' in request.json:
        sweep = request.json['sweep']
        if sweep in ['on','off']:
            valid_commands = True
            york.setSweep(sweep)
        else:
            return jsonify({'error': 'invalid sweep'})


    #verify the temperature parameter
    if 'temp' in request.json:
        temp = request.json['temp']
        if temp in ['16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32']:
            valid_commands = True
            york.setTemp(temp)
        else:
            return jsonify({"error":"invalid temperature"})




    '''
     If any parameter was valid, the code will be executed.
    '''
    if valid_commands:
        controllerCOM.execute(york.getJsonCode());
        return jsonify(york.getJsonCode())
    else:
        return jsonify({'error':'invalid parameters'})





'''
From Here is the main control
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True);


