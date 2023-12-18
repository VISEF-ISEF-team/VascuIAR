using UnityEngine;
using EzySlice;
using UnityEngine.InputSystem; 

public class EnableSlice : MonoBehaviour
{
    public EnableSlice baseEnableSlice;
    private DeleteSliceOnButtonPress baseDeleteSliceOnButtonPress;

    public GameObject heartTarget;
    public Material crossSectionMaterial;

    public GameObject planeObject; 
    private Transform planeCoordinates;

    private void Start()
    {
        planeCoordinates = planeObject.transform; 
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Slice(heartTarget); 
        }
    }

    // normal of a plane is a vector that is perpendicular to the plane
    public void Slice(GameObject target)
    {
        if (GetIntersection(planeObject, 100.0f))
        {
            SlicedHull hull = target.Slice(planeCoordinates.position, planeCoordinates.up);
            Debug.Log(target.name); 
            if (hull != null)
            {
                // upper hull
                GameObject upperHull = hull.CreateUpperHull(target, crossSectionMaterial);
                SliceComponentSetup(upperHull, true, target.name);
                upperHull.transform.position = new Vector3(heartTarget.transform.position.x + 1.5f, heartTarget.transform.position.y, heartTarget.transform.position.z);

                // lower hull
                GameObject lowerHull = hull.CreateLowerHull(target, crossSectionMaterial);
                SliceComponentSetup(lowerHull, false, target.name);
                lowerHull.transform.position = new Vector3(heartTarget.transform.position.x - 1.5f, heartTarget.transform.position.y, heartTarget.transform.position.z);
            }
        }

    }

    public void SliceComponentSetup(GameObject sliceComponent, bool upper, string baseName)
    {
        // set delete on slice
/*        DeleteSliceOnButtonPress currentDeleteSliceOnButtonPressSettings = sliceComponent.AddComponent<DeleteSliceOnButtonPress>();*/

        // set enable slice 
        EnableSlice currentEnableSlice = sliceComponent.AddComponent<EnableSlice>();

        currentEnableSlice.heartTarget = sliceComponent;

        currentEnableSlice.crossSectionMaterial = baseEnableSlice.crossSectionMaterial;

        currentEnableSlice.planeObject = baseEnableSlice.planeObject; 

        currentEnableSlice.baseEnableSlice = baseEnableSlice; 

        // set name for sliced component
        if (upper)
        {
            sliceComponent.name = $"{baseName}-upper";
        }
        else
        {
            sliceComponent.name = $"{baseName}-lower";
        }
    }

    private bool GetIntersection(GameObject planeObject, float numRay)
    {
        return DrawRayXDirection(planeObject, numRay) && DrawRayZDirection(planeObject, numRay);
    }

    private bool DrawRayXDirection(GameObject planeObject, float numberOfRaysEachSide)
    {
        bool forward = false;
        bool backward = false;
        Bounds planeMeshBound = planeObject.GetComponent<MeshFilter>().mesh.bounds;
        Vector3 planeExtents = planeMeshBound.extents;

        float xScale = planeObject.transform.localScale.x;
        float zScale = planeObject.transform.localScale.z;

        float zMaxDistance = planeExtents.z * 2 * zScale;
        float zStep = zMaxDistance / numberOfRaysEachSide;

        float maxZ = planeObject.transform.position.z + (planeExtents.z * zScale);
        float minZ = planeObject.transform.position.z - (planeExtents.z * zScale);

        // positive X direction ray cast, ray then move in Z direction 
        for (int i = 0; i < numberOfRaysEachSide; i++)
        {
            // center.x + extents.x, center.y, center.z + extents.z 
            // then we change what we add to the center.z to move it down
            // each step will be extents.z * 2 * scale / step 

            // positive X
            float newX = planeObject.transform.position.x + (planeExtents.x * xScale);
            float newY = planeObject.transform.position.y;
            float newZ = planeObject.transform.position.z + (planeExtents.z * zScale) - zStep * i;

            Vector3 origin = new Vector3(newX, newY, newZ);

            if (Physics.Raycast(origin, new Vector3(-1, 0, 0), out RaycastHit hit, zMaxDistance))
            {
                Debug.DrawLine(origin, hit.point, Color.green, 100.0f);
                if (!forward) forward = true;
            }
            else
            {
                Debug.DrawLine(origin, new Vector3(planeObject.transform.position.x - (planeExtents.x * xScale), origin.y, origin.z), Color.red, 100.0f);
            }
        }

        for (int i = 0; i < numberOfRaysEachSide; i++)
        {
            // center.x + extents.x, center.y, center.z + extents.z 
            // then we change what we add to the center.z to move it down
            // each step will be extents.z * 2 * scale / step 

            // positive X
            float newX = planeObject.transform.position.x - (planeExtents.x * xScale);
            float newY = planeObject.transform.position.y;
            float newZ = planeObject.transform.position.z + (planeExtents.z * zScale) - zStep * i;

            Vector3 origin = new Vector3(newX, newY, newZ);

            if (Physics.Raycast(origin, new Vector3(1, 0, 0), out RaycastHit hit, zMaxDistance))
            {
                if (!backward) backward = true;
                Debug.DrawLine(origin, hit.point, Color.green, 100.0f);
            }
        }
        return forward && backward;
    }

    private bool DrawRayZDirection(GameObject planeObject, float numberOfRaysEachSide)
    {
        bool forward = false;
        bool backward = false;

        Bounds planeMeshBound = planeObject.GetComponent<MeshFilter>().mesh.bounds;
        Vector3 planeExtents = planeMeshBound.extents;

        float xScale = planeObject.transform.localScale.x;
        float zScale = planeObject.transform.localScale.z;

        float xMaxDistance = planeExtents.x * 2 * xScale;
        float xStep = xMaxDistance / numberOfRaysEachSide;

        for (int i = 0; i < numberOfRaysEachSide; i++)
        {
            float newX = planeObject.transform.position.x + (planeExtents.x * xScale) - xStep * i;
            float newY = planeObject.transform.position.y;
            float newZ = planeObject.transform.position.z + (planeExtents.z * zScale);

            Vector3 origin = new Vector3(newX, newY, newZ);

            if (Physics.Raycast(origin, new Vector3(0, 0, -1), out RaycastHit hit, xMaxDistance))
            {
                if (!forward) forward = true;
                Debug.DrawLine(origin, hit.point, Color.green, 100.0f);
            }
            else
            {
                Debug.DrawLine(origin, new Vector3(origin.x, origin.y, planeObject.transform.position.z - (planeExtents.z * zScale)), Color.red, 100.0f);
            }
        }

        for (int i = 0; i < numberOfRaysEachSide; i++)
        {
            float newX = planeObject.transform.position.x + (planeExtents.x * xScale) - xStep * i;
            float newY = planeObject.transform.position.y;
            float newZ = planeObject.transform.position.z - (planeExtents.z * zScale);

            Vector3 origin = new Vector3(newX, newY, newZ);

            if (Physics.Raycast(origin, new Vector3(0, 0, 1), out RaycastHit hit, xMaxDistance))
            {
                if (!backward) backward = true;
                Debug.DrawLine(origin, hit.point, Color.green, 100.0f);
            }
        }

        return forward && backward;
    }
}
