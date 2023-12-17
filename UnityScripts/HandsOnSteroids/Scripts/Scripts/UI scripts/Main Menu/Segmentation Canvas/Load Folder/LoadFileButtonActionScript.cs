using UnityEditor;
using UnityEngine;
using System.Diagnostics;
using System.Collections;
using Dummiesman;
using System.IO;
using UnityEngine.XR.Interaction.Toolkit;
using System.Collections.Generic;
using UnityEngine.UI; 

#nullable enable
public class LoadFileButtonActionScript : MonoBehaviour
{
    // have another script control all of the buttons in the folder 

    // base material is assigned as asset 
    public Material baseMaterial; 

    // parentObject is the heart segment object in Unity, which is an empty object with scripts only 
    public GameObject parentObject;

    // this field is for setting up disappear and appear buttons
    public SegmentCanvas segmentCanvasControllerScript;

    public GameObject? folderButton;
    public GameObject? fileButton;
    public string stlFolderPath;
    public string stlFilePath;

    public DeleteSliceOnButtonPress baseDeleteSliceOnButtonPressScript;
    public EnableSlice baseEnableSliceOnButtonPressScript;

    private Color singleColor = new Color(22 / 255f, 48 / 255f, 32 / 255f);
    private Dictionary<string, Color> colorDictionary = new Dictionary<string, Color>()
    {
        { "left_ventricle", new Color(241 / 255f, 214 / 255f, 145 / 255f) },
        { "right_ventricle", new Color(216 / 255f, 101 / 255f, 79 / 255f) },
        { "left_atrium", new Color(128 / 255f, 174 / 255f, 128 / 255f) },
        { "right_atrium", new Color(111 / 255f, 184 / 255f, 210 / 255f) },
        { "myocardium",  new Color(220 / 255f, 245 / 255f, 20 / 255f) },
        { "descending_aorta", new Color(250 / 255f, 1 / 255f, 1 / 255f) },
        { "pulmonary_trunk", new Color(244 / 255f, 214 / 255f, 49 / 255f) },
        { "ascending_aorta", new Color(252 / 255f, 129 / 255f, 132 / 255f) },
        { "vena_cava", new Color(13 / 255f, 5 / 255f, 255 / 255f) },
        { "auricle",  new Color(230 / 255f, 220 / 255f, 70 / 255f) },
        { "coronary_artery", new Color(216 / 255f, 101 / 255f, 79 / 255f)}
    };

    private bool folderCoroutineError = false;
    private bool fileCorountineError = false;
    private float scaleFactor = 0.007f;

    private void Start()
    {
        baseDeleteSliceOnButtonPressScript = parentObject.GetComponent<DeleteSliceOnButtonPress>();
        baseEnableSliceOnButtonPressScript = parentObject.GetComponent<EnableSlice>(); 
    }
    private void Update()
    {
        if (folderCoroutineError)
        {
            StopCoroutine(LoadFileCoroutine(stlFolderPath));
            folderCoroutineError = false;
        }

        if (fileCorountineError)
        {
            StopCoroutine(LoadFileCoroutine(stlFilePath));
            fileCorountineError = false;
        }
    }

    public void LoadFolder()
    {
        UnityEngine.Debug.Log("Load Folder");
        if (!string.IsNullOrEmpty(stlFolderPath))
        {
            StartCoroutine(LoadFolderCoroutine(stlFolderPath));
        }
    }

    public void LoadFile()
    {
        if (!string.IsNullOrEmpty(stlFilePath))
        {
            StartCoroutine(LoadFileCoroutine(stlFilePath));
        }
    }

    private IEnumerator LoadFileCoroutine(string stlFilePath)
    {
        string interpreterPath = @"E:\\ISEF\\VasculAR2\\VascuIAR\\.venv\\Scripts\\python.exe";
        string parserFilePath = @"E:\\ISEF\\VasculAR2\\VascuIAR\\UnityScripts\\STLParser\\parse.py";
        string objFilePath = @"E:\\ISEF\\VasculAR2\\VascuIAR\\UnityScripts\\STLParser\\output_file.obj";

        UnityEngine.Debug.Log(stlFilePath);

        yield return null;

        if (!string.IsNullOrEmpty(stlFilePath))
        {
            ProcessStartInfo processStartInfo = new ProcessStartInfo()
            {
                FileName = interpreterPath,
                Arguments = $"{parserFilePath} {stlFilePath}",
                RedirectStandardError = true,
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            };

            using (Process process = new Process { StartInfo = processStartInfo })
            {
                process.Start();
                process.WaitForExit();
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();


                if (!string.IsNullOrEmpty(error))
                {
                    UnityEngine.Debug.Log("Python Script Error:");
                    UnityEngine.Debug.Log(error);
                    fileCorountineError = true;
                    StopCoroutine(LoadFileCoroutine(stlFilePath));
                }
                else if (!string.IsNullOrEmpty(output))
                {
                    UnityEngine.Debug.Log(output);
                    fileCorountineError = true;
                }

                if (HasChildren(parentObject.transform))
                {
                    DeleteChildren(parentObject.transform);
                }

                string loadedObjectName = "";
                string[] parsedName = Path.GetFileNameWithoutExtension(stlFilePath).Split("_");

                if (parsedName.Length > 3)
                {
                    for (int i = 2; i < parsedName.Length; i++)
                    {
                        loadedObjectName += parsedName[i];
                        loadedObjectName += " ";
                    }
                }
                else if (parsedName.Length == 3)
                {
                    loadedObjectName = parsedName[2];
                }
                else
                {
                    loadedObjectName = Path.GetFileNameWithoutExtension(stlFilePath);
                }

                GameObject loadedObject = new OBJLoader().Load(objFilePath);
                loadedObject.name = loadedObjectName;
                loadedObject.transform.position = Vector3.zero;
                loadedObject.transform.localScale = new Vector3(scaleFactor, scaleFactor, scaleFactor);
                MeshRenderer childMeshRenderer = loadedObject.GetComponentInChildren<MeshRenderer>();
                childMeshRenderer.material.color = singleColor;
            }
        }
        else
        {
            fileCorountineError = true;
            yield return null;
        }
    }

    private IEnumerator LoadFolderCoroutine(string stlFolderPath)
    {
        string interpreterPath = @"E:\\ISEF\\VasculAR2\\VascuIAR\\.venv\\Scripts\\python.exe";
        string parserFilePath = @"E:\\ISEF\\VasculAR2\\VascuIAR\\UnityScripts\\STLParser\\parse.py";
        string objFolderPath = @"E:\\ISEF\\VasculAR2\\VascuIAR\\UnityScripts\\STLParser\\\obj_folder\\";

        yield return null;

        if (!string.IsNullOrEmpty(stlFolderPath))
        {
            ProcessStartInfo processStartInfo = new ProcessStartInfo()
            {
                FileName = interpreterPath,
                Arguments = $"{parserFilePath} {stlFolderPath}",
                RedirectStandardError = true,
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            };

            using (Process process = new Process { StartInfo = processStartInfo })
            {
                process.Start();
                process.WaitForExit();
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();


                if (!string.IsNullOrEmpty(error))
                {
                    UnityEngine.Debug.Log("Python Script Error:");
                    UnityEngine.Debug.Log(error);
                    folderCoroutineError = true;
                    StopCoroutine(LoadFileCoroutine(stlFolderPath));
                }
                else if (!string.IsNullOrEmpty(output))
                {
                    UnityEngine.Debug.Log(output);
                    folderCoroutineError = true;
                }

                if (HasChildren(parentObject.transform))
                {
                    DeleteChildren(parentObject.transform);
                }

                string[] objFileList = Directory.GetFiles(objFolderPath);

                // loop through all the file in Object Folder
                foreach (string filePath in objFileList)
                {
                    // initialize object to spawn 
                    string loadedObjectName = Path.GetFileNameWithoutExtension(filePath);

                    GameObject loadedObject = new OBJLoader().Load(filePath);
                    loadedObject.name = loadedObjectName;
                    loadedObject.transform.position = Vector3.zero;
                    loadedObject.transform.localScale = new Vector3(scaleFactor, scaleFactor, scaleFactor);
                    MeshRenderer childMeshRenderer = loadedObject.GetComponentInChildren<MeshRenderer>();
                    Material newMaterial = Instantiate(baseMaterial);
                    newMaterial.color = colorDictionary[loadedObject.name];
                    UnityEngine.Debug.Log(colorDictionary[loadedObject.name]);
                    childMeshRenderer.material = newMaterial;

                    loadedObject.transform.SetParent(parentObject.transform, false);

                    // add grab interactable
                    loadedObject.AddComponent<XRGrabInteractable>();  

                    // initialize delete slice and destroy slice on input
                    DeleteSliceOnButtonPress currentDeleteSliceOnButtonPress = loadedObject.AddComponent<DeleteSliceOnButtonPress>();   
                    EnableSlice currentEnableSlice = loadedObject.AddComponent<EnableSlice>();

                    // set delete slice settings
                    currentDeleteSliceOnButtonPress.deleteButton = baseDeleteSliceOnButtonPressScript.deleteButton;

                    // set enablie slice settings
                    currentEnableSlice.heartTarget = loadedObject; 

                    currentEnableSlice.crossSectionMaterial = baseEnableSliceOnButtonPressScript.crossSectionMaterial;

                    currentEnableSlice.planeCoordinates = baseEnableSliceOnButtonPressScript.planeCoordinates;

                    currentEnableSlice.heartRigidBody = baseEnableSliceOnButtonPressScript.heartRigidBody;

                    segmentCanvasControllerScript.StartSetupProcess(); 
                }
            }
            yield return null;
        }
        else
        {
            folderCoroutineError = true;
            yield return null;
        }
        yield return null;
    }

    public void SetupOnClickListener()
    {
        if (folderButton != null)
        {
            UnityEngine.Debug.Log("folderButton is not null");
            UnityEngine.Debug.Log(stlFolderPath);
            folderButton.GetComponent<Button>().onClick.AddListener(LoadFolder);
        }
        else if (fileButton != null)
        {
            fileButton.GetComponent<Button>().onClick.AddListener(LoadFile);
        }
    }

    private void DeleteChildren(Transform parent)
    {
        // Loop through each child of the parent
        for (int i = parent.childCount - 1; i >= 0; i--)
        {
            // Destroy the child GameObject
            Destroy(parent.GetChild(i).gameObject);
        }
    }

    private bool HasChildren(Transform parent)
    {
        // Check if the parent has any children
        return parent.childCount > 0;
    }
}

