"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)


# Create the Jackson Family Instance
jackson_family = FamilyStructure("Jackson")


# Handle Error
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


#Get all members
@app.route('/members', methods=['GET'])
def getAllMembers():
    members = jackson_family.get_all_members()
    return jsonify(members), 200


#Add member
@app.route('/member', methods=['POST'])
def addMember():
    if not request.data or request.is_json is not True:
        raise APIException('Missing JSON object', status_code=400)

    data = request.json
    memberId = data.get("id", None)

    member = {
        "lucky_numbers": data.get("lucky_numbers", None),
        "first_name": data.get("first_name", None),
        "last_name": jackson_family.last_name,
        "age": data.get("age", None)
    }

    if [x for x in member.values() if not x]:
        raise APIException('Missing parameters', status_code=400)

    if not isinstance(member['lucky_numbers'], list):
        raise APIException('lucky_numbers error format', status_code=400)

    if not isinstance(memberId, int):
        memberId = jackson_family._generateId()

    member["id"] = memberId

    jackson_family.add_member(member)

    return jsonify(""), 200


#Get member by id
@app.route('/member/<int:member_id>', methods=['GET'])
def getMember(member_id):

    member = jackson_family.get_member(member_id)

    if not member: raise APIException('Member not found', status_code=404)
    else: return jsonify(member), 200


#Update member by id
@app.route('/member/<int:member_id>', methods=['PUT'])
def updateMember(member_id):
    if not jackson_family.get_member(member_id):
        raise APIException('Member not found', status_code=404)

    if not request.data or request.is_json is not True:
        raise APIException('Missing JSON object', status_code=400)

    data = request.json
    member = {
        "lucky_numbers": data.get("lucky_numbers", None),
        "first_name": data.get("first_name", None),
        "age": data.get("age", None)
    }

    if [x for x in member.values() if not x]:
        raise APIException('Missing parameters', status_code=400)

    if not isinstance(member['lucky_numbers'], list):
        raise APIException('lucky_numbers error format', status_code=400)

    jackson_family.update_member(member_id, member)

    return jsonify({ "done": True, "member": jackson_family.get_member(member_id)}), 200


# Delete member by id
@app.route('/member/<int:member_id>', methods=['DELETE'])
def deleteMember(member_id):

    member = jackson_family.get_member(member_id)

    if not member:
        raise APIException('Member not found', status_code=404)
    
    jackson_family.delete_member(member_id)

    return jsonify({ "done": True }), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
