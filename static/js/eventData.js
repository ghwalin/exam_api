/**
 *  data handler for events
 */
let eventList = {};

/**
 * reads all events matching a filter
 */
function readEventList(elementIds) {
    sendRequest(API_URL + "/events")
        .then(data => setEventList(data, elementIds))
        .catch(result => {
            showMessage("danger", "Es ist ein Fehler aufgetreten");
        });
}

/**
 * saves the events as an array
 * @param data  the events
 * @param elementIds  array of element-Ids for the events
 */
function setEventList(data, elementIds) {
    (async () => {
        let exists = false;
        while (!exists) {
            exists = document.readyState === "complete";
            if (!exists)
                await new Promise(resolve => setTimeout(resolve, 100));
        }

        let targets = [];
        for (let key in elementIds) {
            targets[key] = document.getElementById(elementIds[key]);
        }
        let sorted = sortEventList(data);
        sorted.forEach(examEvent => {
            let locked = "true";
            let option = document.createElement("option");
            option.value = examEvent.event_uuid;
            if (examEvent.diff !== 0) {
                option.text = eventList[examEvent.event_uuid].timestamp;
                option.setAttribute("data-supervisor", examEvent.supervisors[0]);
                option.setAttribute("data-eventStatus", examEvent.status);
                examEvent.supervisors.forEach(supervisor => {
                    if (supervisor === user) locked = "false";
                });
            } else {
                option.text = "--------";
                option.disabled = true;
            }
            option.setAttribute("data-locked", locked);
            for (let key in targets) {
                let copy = option.cloneNode(true);

                if (targets[key].id === "event_uuid" &&
                    (examEvent.status !== "open" && examEvent.status !== "unassigned")
                ) {
                    copy.disabled = true;
                    copy.setAttribute("data-locked", locked);
                }
                targets[key].appendChild(copy);
            }
        });
        const event_uuid = readStorage("event_uuid");
        if (event_uuid !== null) {
            document.getElementById("dateSearch").value = event_uuid;
            searchExamlist();
        }
        showMessage("clear");
    })();
}

/**
 * sorts the event list
 * @param eventArray
 * @return  sorted array
 */
function sortEventList(eventArray) {
    let future = [];
    let past = [];
    eventArray.forEach(examEvent => {
        let diff = new Date(examEvent.timestamp) - new Date();
        examEvent.diff = diff;
        if (diff < 0) past.push(examEvent);
        else future.push(examEvent);

        const key = examEvent.event_uuid;
        eventList[key] = examEvent;
        if (examEvent.status === 'unassigned') {
            eventList[key].timestamp = 'unbestimmt';
        } else {
            eventList[key].timestamp = new Date(examEvent.timestamp).toLocaleDateString();
        }
    });

    future.sort((a, b) => {
        return a.diff - b.diff;
    });
    past.sort((a, b) => {
        return b.diff - a.diff;
    })

    let sortedArray = future;
    const today = {
        "event_uuid": "",
        "timestamp": "--------",
        "diff": 0,
        "supervisors": [],
        "rooms": []
    };
    sortedArray.push(today);
    sortedArray = sortedArray.concat(past);
    return sortedArray;
}

function saveEvent(data) {
    /**
     * Saves changes to an event
     * @type {string}
     */
    let httpMethod = "PUT";

    const result = sendRequest(API_URL + "/event", httpMethod, data, "text");
    return result;
}