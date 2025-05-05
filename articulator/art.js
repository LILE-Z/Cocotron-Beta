import * as THREE from 'three';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';

let camera, scene, renderer, clock;

const realRanges = {
    head: {
        x: {min: 0, max: 90},
        y: {min: 35, max: 70},
    },
    lupperarm: {
        x: {min: 0, max: 150},
        z: {min: 70, max: 150},
    },
    lforearm: {
        x: {min: 0, max: 90},
    },
    rupperarm: {
        x: {min: 0, max: 150},
        z: {min: 70, max: 150},
    },
    rforearm: {
        x: {min: 0, max: 90},
    },
};
let simulatedRanges = {};
let bodyParts = [];
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2(0, 0);

var selection = null;
var selectionGroup = null;

let framesFolder;
let frames = {};
let poses = [];
let settings = {
    'record pose': recordPose,
    'export sequence': exportSequence,
};

const ANIM_SPEED = 6.0;
const ANIM_ERR = 0.015;

const BODY_PART_MATERIAL = new THREE.MeshLambertMaterial({ color: 0xaaaaaa });
const X_AXIS_MATERIAL = new THREE.MeshLambertMaterial({ color: 0xff2e2e });
const Y_AXIS_MATERIAL = new THREE.MeshLambertMaterial({ color: 0x53e03a });
const Z_AXIS_MATERIAL = new THREE.MeshLambertMaterial({ color: 0x3f7aea });

init();

function init() {
    scene = new THREE.Scene();

    clock = new THREE.Clock();

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setAnimationLoop(animate);
    document.body.appendChild(renderer.domElement);

    // camera
    camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 1000);
    camera.rdata = {
        angle: THREE.MathUtils.degToRad(120),
        radius: 45,
        maxRad: 100,
        minRad: 30,
    };
    updateCam();
    scene.add(camera);

    // ambient light
    scene.add(new THREE.AmbientLight(0x666666));

    // point light
    const light = new THREE.PointLight(0xffffff, 3, 0, 0);
    camera.add(light);

    // helper
    scene.add(new THREE.AxesHelper(20));

    // black charro
    buildBlackCharro(scene);

    // store ranges of each bodypart
    bodyParts.forEach((b) => {
        if (b.bodypartName) {
            simulatedRanges[b.bodypartName] = {};
            b.rdata.data.forEach((ax) => {
                simulatedRanges[b.bodypartName][ax.axis] = {
                    min: Math.round(THREE.MathUtils.radToDeg(ax.min)),
                    max: Math.round(THREE.MathUtils.radToDeg(ax.max)),
                };
            });
        }
    });

    console.log(simulatedRanges);

    buildGUI();

    window.addEventListener('resize', onWindowResize);
    window.addEventListener('mousedown', onClick);
    window.addEventListener('mousemove', function (ev) {
        if (ev.buttons == 1) {
            onMove(ev);
        }
    });
    window.addEventListener('wheel', zoomCam);
}

function rotationData(minmax, axis) {
    let rdata = {
        active: 0,
        data: [],
    };

    if (minmax.length != axis.length) {
        console.error('Make sure there are as many minmax ranges as axis!');
        return;
    }

    Array.from(axis).forEach((ax, i) => {
        rdata.data.push({
            axis: ax,
            min: THREE.MathUtils.degToRad(minmax[i][0]),
            max: THREE.MathUtils.degToRad(minmax[i][1]),
        });
    });

    return rdata;
}

function materialFromRdata(rdata) {
    switch (rdata.data[rdata.active].axis) {
        case 'x': return X_AXIS_MATERIAL;
        case 'y': return Y_AXIS_MATERIAL;
        case 'z': return Z_AXIS_MATERIAL;
    }
}

function buildBlackCharroArm(scene, offsetX, upperarmRanges) {
    const FOREARM_WIDTH = 1.5;
    const ARM_LENGTH = 7;
    const UPPERARM_WIDTH = 1.45;

    const side = (offsetX > 0) ? 'l' : 'r';

    const forearm = new THREE.Mesh(
        new THREE.BoxGeometry(FOREARM_WIDTH, FOREARM_WIDTH, ARM_LENGTH),
        BODY_PART_MATERIAL,
    );
    const upperarm = new THREE.Mesh(
        new THREE.BoxGeometry(UPPERARM_WIDTH, ARM_LENGTH, UPPERARM_WIDTH),
        BODY_PART_MATERIAL,
    );

    forearm.rdata = rotationData([[0, 90]], 'x');
    forearm.geometry.translate(0, 0, 2.8);
    forearm.bodypartName = side + 'forearm';
    forearm.animate = false;

    upperarm.rdata = rotationData(upperarmRanges, 'xz');
    upperarm.position.set(0, 7, 0);
    upperarm.geometry.translate(0, -3, 0);
    upperarm.bodypartName = side + 'upperarm';
    upperarm.animate = false;

    forearm.translateY(-7);
    upperarm.translateY(-7);

    let arm = new THREE.Group();
    upperarm.selectionGroup = arm;
    arm.translateY(8);
    arm.translateX(offsetX);
    arm.add(forearm);
    arm.add(upperarm);

    bodyParts.push(forearm);
    bodyParts.push(upperarm);
    bodyParts.push(arm);

    scene.add(arm);
}

function buildBlackCharro(scene) {
    buildBlackCharroArm(scene, -5.5, [[-90, 90], [-150, 0]]);
    buildBlackCharroArm(scene, 5.5, [[-90, 90], [0, 150]]);

    const body = new THREE.Mesh(
        new THREE.BoxGeometry(8, 12, 3),
        BODY_PART_MATERIAL,
    );
    body.translateY(3);
    scene.add(body);

    const head = new THREE.Mesh(
        new THREE.BoxGeometry(5, 5, 5),
        BODY_PART_MATERIAL,
    );
    head.translateY(12);
    head.rdata = rotationData([[-45, 45], [-30, 20]], 'yx');
    head.bodypartName = 'head';
    head.animate = false;
    bodyParts.push(head);
    scene.add(head);
}

function buildGUI() {
    const pannel = new GUI({ width: 250 });
    pannel.add(settings, 'record pose');
    pannel.add(settings, 'export sequence');
    framesFolder = pannel.addFolder('Frames');
}

function getRotations() {
    let frame = {};
    let part;
    bodyParts.forEach((b) => {
        if (b.bodypartName != undefined) {
            const r = function(part, ax) {
                switch (ax) {
                    case 'x': return part.rotation.x;
                    case 'y': return part.rotation.y;
                    case 'z': return part.rotation.z;
            }};

            frame[b.bodypartName] = {};
            part = (b.selectionGroup) ? b.selectionGroup : b;
            b.rdata.data.forEach((d) => {
                // frame[b.bodypartName][d.axis] = r(part, d.axis);
                frame[b.bodypartName][d.axis] = part.rotation[d.axis];
            });
        }
    });

    return frame;
}

function recordPose() {
    const frame = getRotations();
    const i = poses.length;

    poses.push(frame);
    frames[i] = function() { setPose(frame); }
    framesFolder.add(frames, i);
}

function setPose(frame) {
    let target;

    bodyParts.forEach((b) => {
        if (b.bodypartName) {
            target = (b.selectionGroup) ? b.selectionGroup : b;
            let anim = {}
            Object.keys(frame[b.bodypartName]).forEach((k) => {
                anim[k] = frame[b.bodypartName][k];
            });
            target.animate = anim;
        }
    });
}

function exportSequence() {
    let output = [...poses];
    output.forEach((pose) => {
        Object.keys(pose).forEach((k) => {
            Object.keys(pose[k]).forEach((ax) => {
                pose[k][ax] = scale(
                    THREE.MathUtils.radToDeg(pose[k][ax]),
                    simulatedRanges[k][ax].min,
                    simulatedRanges[k][ax].max,
                    realRanges[k][ax].min,
                    realRanges[k][ax].max,
                );
                // pose[k][ax] = THREE.MathUtils.radToDeg(pose[k][ax]);
            });
        });
    });

    // https://stackoverflow.com/questions/45831191/generate-and-download-file-from-js
    let filename = 'secuencia.json';
    let element = document.createElement('a');
    let json = JSON.stringify(output, null, 4);

    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(json));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function onClick(ev) {
    let m = {
        x: (ev.clientX / renderer.domElement.clientWidth) * 2 - 1,
        y: - (ev.clientY / renderer.domElement.clientHeight) * 2 + 1,
    };

    mouse.x = ev.clientX;
    mouse.y = ev.clientY;

    raycaster.setFromCamera(m, camera);

    var intersects = raycaster.intersectObjects(bodyParts, false);
    if (intersects.length > 0) {
        if (selection === null) {
            selection = intersects[0].object;
            if (selection.selectionGroup) {
                selectionGroup = selection.selectionGroup;
            }
            selection.material = materialFromRdata(selection.rdata);

        } else if (selection === intersects[0].object) {
            if (selection.rdata.data.length > 1) {
                selection.rdata.active++;

                if (selection.rdata.active == selection.rdata.data.length) {
                    selection.rdata.active = 0;
                    selection.material = BODY_PART_MATERIAL;
                    selection = null;
                    selectionGroup = null;
                } else {
                    selection.material = materialFromRdata(selection.rdata);
                }
            } else {
                selection.material = BODY_PART_MATERIAL;
                selection = null;
                selectionGroup = null;
            }

        } else {
            selection.material = BODY_PART_MATERIAL;
            selection = intersects[0].object;
            if (selection.selectionGroup) {
                selectionGroup = selection.selectionGroup;
            } else {
                selectionGroup = null;
            }
            selection.material = materialFromRdata(selection.rdata);
        }
    }
}

function onMove(ev) {
    if (selection !== null) {
        moveBodyPart(ev);
    } else {
        rotateCam(ev);
    }

    mouse.x = ev.clientX;
    mouse.y = ev.clientY;
}

function moveBodyPart(ev) {
    var d = mouse.clone().sub(new THREE.Vector2(ev.clientX, ev.clientY)).length() * 0.01;
    d = THREE.MathUtils.clamp(d, 0, 3)
    if (ev.clientY > mouse.y) {
        d *= -1;
    }

    let target;
    if (selectionGroup !== null) {
        target = selectionGroup;
        target.rdata = selection.rdata;
    } else {
        target = selection;
    }

    let axData = target.rdata.data[target.rdata.active];

    switch (axData.axis) {
        case 'x':
            var dx = target.rotation.x + d;
            target.rotation.set(
                THREE.MathUtils.clamp(dx, axData.min, axData.max),
                target.rotation.y,
                target.rotation.z
            );
            break;
        case 'y':
            var dy = target.rotation.y + d;
            target.rotation.set(
                target.rotation.x,
                THREE.MathUtils.clamp(dy, axData.min, axData.max),
                target.rotation.z
            );
            break;
        case 'z':
            var dz = target.rotation.z + d;
            target.rotation.set(
                target.rotation.x,
                target.rotation.y,
                THREE.MathUtils.clamp(dz, axData.min, axData.max),
            );
            break;
        default:
            console.error('wtf is ax ' + axData.axis + ' ?');
            break;
    }
}

function updateCam() {
    camera.position.set(
        Math.cos(camera.rdata.angle) * camera.rdata.radius,
        20,
        Math.sin(camera.rdata.angle) * camera.rdata.radius,
    );
    camera.lookAt(new THREE.Vector3(0, 5, 0));
}

function rotateCam(ev) {
    var d = mouse.clone().sub(new THREE.Vector2(ev.clientX, ev.clientY)).length() * 0.01;
    d = THREE.MathUtils.clamp(d, 0, 3)
    if (ev.clientX < mouse.x) {
        d *= -1;
    }

    camera.rdata.angle = (camera.rdata.angle + d) % 360;
    updateCam();
}

function zoomCam(ev) {
    camera.rdata.radius = THREE.MathUtils.clamp(
        camera.rdata.radius + (ev.deltaY * 0.1),
        camera.rdata.minRad,
        camera.rdata.maxRad,
    );
    updateCam();
}

function animate() {
    bodyParts.forEach((b) => {
        if (b.animate) {
            let done = true;
            Object.keys(b.animate).forEach((k) => {
                let diff = b.animate[k] - b.rotation[k];
                let ndiff = diff / Math.abs(diff);

                if (Math.abs(diff) < ANIM_ERR) {
                    b.rotation[k] = b.animate[k];
                } else {
                    b.rotation[k] += ndiff * ANIM_SPEED * clock.getDelta();
                    done = false;
                }
            });

            if (done) {
                b.animate = false;
            }
        }
    });

    renderer.render(scene, camera);
}

/**
 * Interpolates a value in range a{min/max} to range b{min/max}.
 */
function scale(val, amin, amax, bmin, bmax) {
    const percent = (val - amin) / (amax - amin);
    return percent * (bmax - bmin) + bmin;
}
