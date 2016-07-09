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

    #verify the status parameter
    if 'status' in request.json:
        status = request.json['status']
        if status == 'on' or status == 'off':
            valid_commands = True
            york.setStatus(status)
        else:
            return jsonify({'error':'invalid status'})


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


