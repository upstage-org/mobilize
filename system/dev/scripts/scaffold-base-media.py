import os
import sys
import shutil
from tokenize import Number
from graphql_server import json_encode
from PIL import Image

appdir = os.path.abspath(os.path.dirname(__file__))
projdir = os.path.abspath(os.path.join(appdir, '../../..'))
if projdir not in sys.path:
    sys.path.append(appdir)
    sys.path.append(projdir)
    
from sqlalchemy import not_
from asset.models import Asset, AssetType, Stage, StageAttribute
from licenses.models import AssetLicense, AssetUsage
from performance_config.models import ParentStage, Performance, Scene
from user.models import ADMIN, GUEST, User
from event_archive.db import build_pg_session
from event_archive.models import Event
from terminal_colors import bcolors
from config.settings import UPLOAD_USER_CONTENT_FOLDER, ENV_TYPE
from config.models import Config
from auth.fernet_crypto import encrypt

'''
if ENV_TYPE == 'Production':
    print(bcolors.FAIL + "This script is not meant to be run in production." + bcolors.ENDC)
    exit()
'''

demo_media_folder = 'ui/static/demo'
owner_id = 0

while not os.path.exists(demo_media_folder):
    demo_media_folder = input(bcolors.WARNING + "The folder \"{}\" does not exist. Please put all demo media you wish to scaffold inside that folder, or enter a custom folder to scaffold from: ".format(demo_media_folder) + bcolors.ENDC)

session = build_pg_session()

while not owner_id:
    username = input(bcolors.BOLD + "Please enter the username of the owner whose these base media belong to: " + bcolors.ENDC)
    owner = session.query(User).filter(User.username == username).first()
    if not owner:
        print("❌ The user \"{}\" does not exist.".format(username))
    else:
        owner_id = owner.id

def scan_demo_folder():
    for type in os.listdir(demo_media_folder):
        if '.' not in type:
            for media in os.listdir("{}/{}".format(demo_media_folder, type)):
                yield type, media

created_media_ids = []
upload_assets_folder = '{}'.format(UPLOAD_USER_CONTENT_FOLDER)

def copy_file(src_path, dest_path, type):
    if not os.path.exists(os.path.join(upload_assets_folder, type)):
        os.makedirs(os.path.join(upload_assets_folder, type))
    shutil.copyfile(src_path, os.path.join(upload_assets_folder, dest_path))

def detect_size(type, path):
    if type == 'stream':
        size = path.split('.')[0].split('_')[-1].split('x')
        if len(size) == 2:
            return down_size(size)
        else:
            print("❌ Please put the video dimension in the stream name, otherwise stream will have square frame. For example \"Demo stream_800x600.mp4\". Current name: {}{}{}".format(bcolors.FAIL, path, bcolors.ENDC))
            return 100, 100
    else:
        with Image.open(path) as img:
            return down_size(img.size)

def down_size(size):
    w = int(size[0])
    h = int(size[1])
    if w > h:
        w = 100
        h = 100 * h / w
    else:
        h = 100
        w = 100 * w / h
    return w, h

def create_media(type, path):
    asset_type = session.query(AssetType).filter(AssetType.name == type).first()
    if not asset_type:
        asset_type = AssetType(name=type)
        session.add(asset_type)
        session.commit()

    asset = Asset(asset_type=asset_type, owner_id=owner_id)
    attributes = {}
    size = 0
    if '.' in path:
        asset.name = os.path.basename(path).split('.')[0]
        # copy asset to uploads folder
        src_path = os.path.join(demo_media_folder, type, path)
        dest_path = os.path.join(type, path)
        copy_file(src_path, dest_path, type)
        asset.file_location = dest_path
        size += os.path.getsize(src_path)
        if type != 'audio' and path[0] != '.':
            attributes['w'], attributes['h'] = detect_size(type, src_path)
    else:
        attributes['multi'] = True
        asset.name = path
        for frame in os.listdir(os.path.join(demo_media_folder, type, path)):
            src_path = os.path.join(demo_media_folder, type, path, frame)
            dest_path = os.path.join(type, "{}_{}".format(path, frame))
            copy_file(src_path, dest_path, type)
            size += os.path.getsize(src_path)
            if not asset.file_location:
                asset.file_location = dest_path
                attributes['frames'] = []
                attributes['w'], attributes['h'] = detect_size(type, src_path)
            attributes['frames'].append(dest_path)

    asset.description = json_encode(attributes)
    asset.size = size
    session.add(asset)
    session.commit()
    created_media_ids.append(asset.id)
    print("✅ Created{} {} {}".format(' multi-frame' if 'multi' in attributes else '', type, path))

def create_demo_media():
    for type, path in scan_demo_folder():
        create_media(type, path)

def create_demo_stage():
    if session.query(Stage).filter(Stage.name == 'Demo').first():
        print("❌ A stage named \"Demo\" already exists.")
        return
    stage = Stage(name='Demo Stage', owner_id=owner_id, description='This is a demo stage to help you learn how to use and customise UpStage for your own performances.', file_location='demo')
    status = StageAttribute(name='status', description='live', stage=stage)
    stage.attributes.append(status)

    visibility = StageAttribute(name='visibility', description='1', stage=stage)
    stage.attributes.append(visibility)

    cover_src = os.path.join(demo_media_folder, 'demo-stage-cover.jpg')
    cover_path = os.path.join('media', 'demo-stage-cover.jpg')
    copy_file(cover_src, cover_path, 'media')
    cover = StageAttribute(name='cover', description=cover_path, stage=stage)
    stage.attributes.append(cover)

    all_users = [x.id for x in session.query(User.id).all()]
    accesses = [[],all_users]
    player_access = StageAttribute(name='playerAccess', description=json_encode(accesses), stage=stage)
    stage.attributes.append(player_access)

    session.add(stage)
    session.commit()
    for media_id in created_media_ids:
        session.add(ParentStage(stage_id=stage.id, child_asset_id=media_id))
    session.commit()
    print("✅ Created demo stage")

def create_demo_users():
    # - Super Admin: with email address support@upstage.live
    # - Guest: one guest account?
    # - Probably no other users as default 
    admin_username = 'admin'
    guest_username = 'guest'
    test_user_password = '12345678'

    if session.query(User).filter(User.username == admin_username).first():
        print("❌ A user named \"{}\" already exists.".format(admin_username))
    else:
        admin = User()
        admin.username = admin_username
        admin.password = encrypt(test_user_password)
        admin.email = "support@upstage.live"
        admin.role = ADMIN
        admin.active = True
        session.add(admin)
        print("✅ Created admin account with credentials: \"{}\" and password \"{}\"".format(admin_username, test_user_password))
    
    if session.query(User).filter(User.username == guest_username).first():
        print("❌ A user named \"{}\" already exists.".format(guest_username))
    else:
        guest = User()
        guest.username = guest_username
        guest.password = encrypt(test_user_password)
        guest.role = GUEST
        guest.active = True
        session.add(guest)
        print("✅ Created guest account with credentials: \"{}\" and password \"{}\"".format(guest_username, test_user_password))

    session.commit()

def save_config(name, value):
    config = session.query(Config).filter(Config.name == name).first()
    if config:
        config.value = value
    else:
        config = Config(name=name, value=value)
        session.add(config)
    session.commit()

def scaffold_foyer():
    save_config('FOYER_TITLE', 'Your New UpStage')
    save_config('FOYER_DESCRIPTION', 'Welcome to your new UpStage! Click on the "Customise Foyer" above to change this message and other settings on this Foyer, then go to the Backstage to get started creating your cyberformance!')
    print("✅ Foyer Scaffolding Completed")

def scaffold_system_configuration():
    save_config('TERMS_OF_SERVICE', 'https://raw.githubusercontent.com/upstage-org/upstage/main/LICENSE')
    save_config('MANUAL', 'https://docs.upstage.live')
    print("✅ System Configuration Scaffolding Completed")

create_demo_media()
create_demo_stage()
create_demo_users()
scaffold_foyer()
scaffold_system_configuration()
