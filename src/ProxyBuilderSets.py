import maya.cmds as mc
from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton

def IsMesh(obj):
    shapes = mc.listRelatives(obj, s=True)
    if not shapes:
        return False
    for s in shapes:
        if mc.objectType(s) == "mesh":
            return True
    return False

def IsSkin(obj):
    return mc.objectType(obj) == "skinCluster"

def IsJoint(obj):
    return mc.objectType(obj) == "joint"

def GetUpperStream(obj):
    return mc.listConnections(obj, s=True, d=False, sh=True)

def GetAllConnectionIn(obj, NextFunc, Filter = None):
    AllFound = set()
    nexts = NextFunc(obj)
    while nexts:
        for next in nexts:
            AllFound.add(next)
        nexts = NextFunc(nexts)
        if nexts:
            nexts = [x for x in nexts if x not in AllFound]        
    if not Filter:
        return list(AllFound)
    filted = []
    for found in AllFound:
        if Filter(found):
            filted.append(found)
    return filted

def GetJntWithMostInfluence(vert, skin):
    weights = mc.skinPercent(skin, vert, q=True, v=True)
    jnts = mc.skinPercent(skin, vert, q=True, t=None)
    maxWeightIndex = 0
    maxWeight = weights[0]
    for i in range(1, len(weights)):
        if weights[i] > maxWeight:
            maxWeight = weights[i]
            maxWeightIndex = i
    return jnts[maxWeightIndex]

class BuildProxy:
    def __init__(self):
        self.skin = ""
        self.model = ""
        self.jnts = []

    def BuildProxyForSelectedmesh(self):
        model = mc.ls(sl=True)[0]
        if not IsMesh(model):
            print("Please select a model")
            return

        self.model = model
        model_shapes = mc.listRelatives(self.model, s=True) or []
        for model_shape in model_shapes:
            materials = mc.listConnections(model_shape, type='shadingEngine')
            if not materials:
                continue

            for material in materials:
                material_name = mc.ls(mc.listConnections(material + '.surfaceShader'))[0]

                self.BuildProxyForMaterial(material_name, model_shape)

    def BuildProxyForMaterial(self, material_name, model_shape):
        self.skin = ''
        self.jnts = []

        existing_skin_clusters = mc.listConnections(model_shape, type='skinCluster')
        if existing_skin_clusters:
            print(f"Proxy mesh '{model_shape}' is already connected to a skinCluster. Skipping material '{material_name}'.")
            return

        skin = mc.listConnections(model_shape, type='skinCluster')
        if skin:
            self.skin = skin[0]
        else:
            intermediate_shapes = mc.ls(mc.listHistory(model_shape, future=True), type='mesh', intermediateObjects=True)
            for intermediate_shape in intermediate_shapes:
                skin = mc.listConnections(intermediate_shape, type='skinCluster')
                if skin:
                    self.skin = skin[0]
                    break

        if not self.skin:
            print(f"No skin cluster found for model shape '{model_shape}'. Skipping.")
            return

        jnts = GetAllConnectionIn(model_shape, GetUpperStream, IsJoint)
        if jnts:
            self.jnts = jnts

        proxy_grp_name = self.model + "_" + material_name + "_proxy_grp"
        if mc.objExists(proxy_grp_name):
            print(f"Proxy group '{proxy_grp_name}' already exists. Skipping material '{material_name}'.")
            return

        jnt_verts_map = self.GenerateJntVertsDict()
        
        segments = []
        ctrls = []

        for jnt, verts in jnt_verts_map.items():
            new_seg = self.CreateProxyModelForMaterial(material_name, model_shape)
            if new_seg is None:
                continue

            if mc.listConnections(new_seg, type="skinCluster"):
                print(f"Proxy mesh '{new_seg}' is already connected to a skinCluster. Skipping.")
                mc.delete(new_seg)  # Delete the duplicate proxy mesh
                continue

            new_skin_cluster = mc.skinCluster(self.jnts, new_seg)[0]
            mc.copySkinWeights(ss=self.skin, ds=new_skin_cluster, nm=True, sa="closestPoint", ia="closestJoint")
            segments.append(new_seg)
            ctrl_loc = "ac_" + jnt + "_proxy"
            mc.spaceLocator(n=ctrl_loc)
            ctrl_loc_grp = ctrl_loc + "_grp"
            mc.group(ctrl_loc, n=ctrl_loc_grp)
            mc.matchTransform(ctrl_loc_grp, jnt)
            
            mc.addAttr(ctrl_loc, ln="vis", min=0, max=1, dv=1, k=True)
            mc.connectAttr(ctrl_loc + ".vis", new_seg + ".v")
            ctrls.append(ctrl_loc_grp)

        proxy_top_grp = proxy_grp_name
        mc.group(segments, n=proxy_top_grp)

        ctrl_top_group = "ac_" + self.model + "_" + material_name + "_proxy_grp"
        mc.group(ctrls, n=ctrl_top_group)

        global_proxy_ctrl = "ac_" + self.model + "_" + material_name + "_proxy_global"
        mc.circle(n=global_proxy_ctrl, r=20)
        mc.parent(proxy_top_grp, global_proxy_ctrl)     
        mc.parent(ctrl_top_group, global_proxy_ctrl)   
        mc.setAttr(proxy_top_grp + ".inheritsTransform", 0)

        mc.addAttr(global_proxy_ctrl, ln="vis", min=0, max=1, k=True, dv=1)
        mc.connectAttr(global_proxy_ctrl + ".vis", proxy_top_grp + ".v")

    def CreateProxyModelForMaterial(self, material_name, model_shape):
        if not mc.objExists(model_shape):
            print(f"Model shape '{model_shape}' does not exist. Skipping material '{material_name}'.")
            return None

        # Duplicate the selected mesh
        dup = mc.duplicate(model_shape, ic=True, rr=True)[0]
        if not dup:
            print(f"Failed to duplicate model shape '{model_shape}'. Skipping material '{material_name}'.")
            return None

        # Get all faces associated with the material
        faces_to_delete = []
        shader_group = mc.listConnections(material_name + '.outColor')[0]
        if shader_group:
            faces = mc.sets(shader_group, q=True)
            if faces:
                all_faces = mc.ls(dup + ".f[*]", flatten=True)
                for face in all_faces:
                    if face not in faces:
                        faces_to_delete.append(face)

        # Delete the faces not associated with the material
        if faces_to_delete:
            mc.delete(faces_to_delete)

        # Return the duplicate mesh with only the selected faces
        return dup

    def GenerateJntVertsDict(self):
        jnt_verts_dict = {}
        for jnt in self.jnts:
            jnt_verts_dict[jnt] = []

        verts = mc.ls(f"{self.model}.vtx[*]", flatten=True)
        for vert in verts:
            owning_jnt = GetJntWithMostInfluence(vert, self.skin)
            jnt_verts_dict[owning_jnt].append(vert)

        return jnt_verts_dict
    

class BuildProxyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.setWindowTitle("Build Rig Proxy") 
        self.setGeometry(0,0,100,100)
        buildBtn = QPushButton("Build Proxy")
        buildBtn.clicked.connect(self.BuildProxyBtnClicked)
        self.masterLayout.addWidget(buildBtn)
        self.adjustSize()
        
        self.builder = BuildProxy()

    def BuildProxyBtnClicked(self):
        self.builder.BuildProxyForSelectedmesh()

buildProxyWidget = BuildProxyWidget()
buildProxyWidget.show()
