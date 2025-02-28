import numpy as np
import matplotlib.pyplot as plt


def standardize_bbox(pcl, points_per_object):
    if points_per_object > pcl.shape[0]:
        points_per_object = pcl.shape[0]
    pt_indices = np.random.choice(pcl.shape[0], points_per_object, replace=False)
    np.random.shuffle(pt_indices)
    pcl = pcl[pt_indices]  # n by 3
    mins = np.amin(pcl, axis=0)
    maxs = np.amax(pcl, axis=0)
    center = (mins + maxs) / 2.
    scale = np.amax(maxs - mins)
    print("Center: {}, Scale: {}".format(center, scale))
    result = ((pcl - center) / scale).astype(np.float32)  # [-0.5, 0.5]
    return result


xml_head = \
    """
<scene version="0.6.0">
    <integrator type="path">
        <integer name="maxDepth" value="-1"/>
    </integrator>
    <sensor type="perspective">
        <float name="farClip" value="100"/>
        <float name="nearClip" value="0.1"/>
        <transform name="toWorld">
            <lookat origin="3,3,3" target="0,0,0" up="0,0,1"/>
        </transform>
        <float name="fov" value="25"/>
        
        <sampler type="ldsampler">
            <integer name="sampleCount" value="256"/>
        </sampler>
        <film type="hdrfilm">
            <integer name="width" value="512"/>
            <integer name="height" value="512"/>
            <rfilter type="gaussian"/>
            <boolean name="banner" value="false"/>
        </film>
    </sensor>
    
    <bsdf type="roughplastic" id="surfaceMaterial">
        <string name="distribution" value="ggx"/>
        <float name="alpha" value="0.05"/>
        <float name="intIOR" value="1.46"/>
        <rgb name="diffuseReflectance" value="1,1,1"/> <!-- default 0.5 -->
    </bsdf>
    
"""

# "0.025"

xml_ball_segment = \
    """
    <shape type="sphere">
        <float name="radius" value="{}"/>
        <transform name="toWorld">
            <translate x="{}" y="{}" z="{}"/>
        </transform>
        <bsdf type="diffuse">
            <rgb name="reflectance" value="{},{},{}"/>
        </bsdf>
    </shape>
"""

xml_tail = \
    """
    <shape type="rectangle">
        <ref name="bsdf" id="surfaceMaterial"/>
        <transform name="toWorld">
            <scale x="10" y="10" z="1"/>
            <translate x="0" y="0" z="-0.5"/>
        </transform>
    </shape>
    
    <shape type="rectangle">
        <transform name="toWorld">
            <scale x="10" y="10" z="1"/>
            <lookat origin="-4,4,20" target="0,0,0" up="0,0,1"/>
        </transform>
        <emitter type="area">
            <rgb name="radiance" value="6,6,6"/>
        </emitter>
    </shape>
</scene>
"""


def colormap(x, y, z):
    vec = np.array([x, y, z])
    vec = np.clip(vec, 0.001, 1.0)
    norm = np.sqrt(np.sum(vec ** 2))
    vec /= norm
    return [vec[0], vec[1], vec[2]]


def read_txt(path):
    pts = []
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split(' ')
            line = [float(l) for l in line]
            _, x, y, z = line
            pts.append([x, y, z])
    pts = np.array(pts).astype(np.float32)
    # print(pts.shape)
    # plt.figure(1)
    # plt.scatter(pts[:, 0], pts[:, 1])
    # plt.show()
    return pts


def main():
    xml_segments = [xml_head]

    pcl = np.load('chair_pcl.npy')
    # pcl = read_txt('./data/lines_arcs_3d_n106_exemplar.txt')

    pcl = standardize_bbox(pcl, 2048)
    # print('1:', pcl.shape, pcl.min(), pcl.max())

    pcl = pcl[:, [2, 0, 1]]
    # print('2:', pcl.shape, pcl.min(), pcl.max())

    pcl[:, 0] *= -1
    # print('3:', pcl.shape, pcl.min(), pcl.max())

    base_radius = 0.025
    coord_scale = 1.25   # changed be changed
    # shift = 0.0125
    shift = 0.0125
    pcl[:] *= coord_scale
    pcl[:, 2] += shift
    print('4:', pcl.shape, pcl.min(), pcl.max())

    for i in range(pcl.shape[0]):
        color = colormap(pcl[i, 0] + 0.5 * coord_scale, pcl[i, 1] + 0.5 * coord_scale, pcl[i, 2] + 0.5 * coord_scale - shift)
        xml_segments.append(xml_ball_segment.format(base_radius * coord_scale, pcl[i, 0], pcl[i, 1], pcl[i, 2], *color))
    xml_segments.append(xml_tail)

    xml_content = str.join('', xml_segments)

    with open('mitsuba_scene.xml', 'w') as f:
        f.write(xml_content)


if __name__ == '__main__':
    main()
