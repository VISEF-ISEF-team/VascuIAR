using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI; 

public class BaseObjectControllerScript : MonoBehaviour
{
    [SerializeField] GameObject resetPositionButton;
    public List<GameObject> childSegmentObjectList;

    public List<Transform> oldPosition;

    private void Start()
    {
        if (resetPositionButton != null && childSegmentObjectList.Count > 0)
        {
            resetPositionButton.GetComponent<Button>().onClick.AddListener(OnResetPositionButtonClick);
        }
    }
    public void OnResetPositionButtonClick()
    {
        for (int i = 0; i < childSegmentObjectList.Count; i++)
        {
            childSegmentObjectList[i].transform.position = oldPosition[i].position;
        }
    }

    // relative positioning and snapping into place
}