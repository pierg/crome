import React from 'react';
import {Link} from "react-router-dom";

function WorldView(props) {
    function arrayBufferToBase64( buffer ) {
        let binary = '';
        let bytes = new Uint8Array( buffer );
        let len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode( bytes[ i ] );
        }
        return binary;
    }

    return(
        <>
            <div onClick={props.onClick} className={"w-full lg:w-6/12 xl:w-5/12 mt-8 ml-4 mr-4 px-4 relative flex cursor-pointer flex-col min-w-0 break-words border-lightBlue-700 bg-white rounded mb-6 xl:mb-0 shadow-lg opacity-1 transform duration-300 transition-all ease-in-out "
                + (props.selected ? "world-border-8" : "world-border-0")}>
                <div className="flex-auto p-4 pr-0">
                    <div className="flex">
                        <div className="flex flex-wrap w-full">
                            <div className="flex flex-wrap">
                                <div className="relative w-full pr-4 max-w-full flex-grow flex-1">
                                    <span className="font-bold text-xl uppercase text-blueGray-700">{props.title}</span>
                                </div>
                            </div>
                            <div className="flex flex-col flex-wrap w-full">
                                <div className="relative w-full pr-4 mt-2 mb-2 max-w-full flex-grow flex-1">
                                <span className="text-md text-blueGray-700">
                                    {props.description}
                                </span>
                                </div>
                                <div className="relative w-full pr-4 max-w-full flex-grow flex-1"/>
                            </div>
                            <div className="w-full">
                                <img src={"data:image/png;base64," + arrayBufferToBase64(props.image)} alt={"World"} className="w-full"/>
                            </div>
                        </div>
                        <div className="flex flex-col min-content">
                            <div className="relative pl-4 flex justify-end flex-initial">
                                <Link to="/world" className="hover-no-underline"><div
                                    onClick={() => props.modify(props.number)}
                                    className={
                                        "text-white p-3 text-center inline-flex items-center justify-center w-12 h-12 shadow-lg rounded-full cursor-pointer " +
                                        props.statIconColor
                                    }
                                >
                                    <i className={props.statIconName}/>
                                </div></Link>
                            </div>
                            {props.number !== 0 && (<div className="relative pl-4 flex mt-2 justify-end flex-initial">
                                <div
                                    onClick={() => props.delete(true, props.number)}
                                    id={"deleteButton"}
                                    className={
                                        "text-white p-3 text-center inline-flex items-center justify-center w-12 h-12 shadow-lg rounded-full cursor-pointer " +
                                        props.statIconColor
                                    }
                                >
                                    <i className={props.statSecondIconName} id={"deleteIcon"}/>
                                </div>
                            </div>)}
                        </div>
                    </div>
                    <div className="flex flex-col mt-4">
                        <div className="relative w-full max-w-full flex-grow flex-1">
                            <div
                                className={"overflow-hidden relative flex flex-col min-w-0 break-words bg-white w-full border-b border-blueGray-200"}>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default WorldView;