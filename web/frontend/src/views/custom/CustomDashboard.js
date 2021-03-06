import React from "react";
import {useLocation} from "react-router-dom";

// components
import CustomSidebar from "components/Crome/CustomSidebar";
import CustomPlayer from "./CustomPlayer";

// texts as props
import customsidebar from "../../_texts/custom/customsidebar";
import custommediaplayerteaminfo from "_texts/custom/customplayerinfo.js";
import {SocketProvider} from "../../contexts/SocketProvider";
import useLocalStorage from "../../hooks/useLocalStorage";
import CreateEnvironment from "./CreateEnvironment";
import Console from "../../components/Crome/Console";
import consoleinfo from "../../_texts/custom/console";
import SocketIoConsoleMessage from "../../components/Custom/Examples/GetConsoleMessage";
import SocketSaveEnvironment from "../../components/Custom/Examples/SaveEnvironment";


export default function CustomDashboard(props) {
    const location = useLocation();
    const [id, setId] = useLocalStorage('id');
    let [message, setMessage] = React.useState("");
    let [world, setWorld] = React.useState(null);
    let [savedEnvironment, setSavedEnvironment] = React.useState(null);
    let [listOfWorldNames, setListOfWorldNames] = React.useState(null);
    let [projectId, setProjectId] = React.useState(null);
    let [triggerSave, setTriggerSave] = React.useState(false);

    function updateMessage(msg) {
        if (message === "") {
            setMessage(msg);
        }
        else {
            setMessage(message + "\n" + msg);
        }
    }
    function updateWorld(wor) {
        setWorld(wor);
    }
    function saveEnvironment(info, env) {
        setSavedEnvironment({"info":info, "environment":env})
        setTriggerSave(true)
    }
    function updateListOfWorldNames(names) {
        setListOfWorldNames(names)
    }

    React.useEffect(() => {
        window.scrollTo(0, 0);
    }, [location]);
    return (
        <SocketProvider id={id}>
            <CustomSidebar {...customsidebar} currentRoute={"#" + location.pathname} id={id} setId={setId}/>
            <Console {...consoleinfo} customText={message}/>
            <SocketIoConsoleMessage modifyMessage={(e) => updateMessage(e)} session={id}/>
            <SocketSaveEnvironment session={id} world={savedEnvironment} trigger={triggerSave} returnProjectId={setProjectId} setTrigger={setTriggerSave}/>
            <div className="relative xxl:ml-64 bg-blueGray-100 min-h-screen">
                {(() => {
                    switch (props.page) {
                        case 'world':
                            return (
                                <CreateEnvironment world={world} session={id} worldNames={listOfWorldNames} returnedProjectId={projectId} resetProject={() => setProjectId(null)} saveEnvironment={saveEnvironment}/>
                            )
                        default:
                            return (
                                <CustomPlayer world={world} {...custommediaplayerteaminfo} setWorld={updateWorld} setListOfWorldNames={updateListOfWorldNames} id={id}/>
                            )
                    }
                })()}
            </div>
        </SocketProvider>
    );
}
