import React, { useState } from 'react';
import UploadVideoForm from '../forms/UploadVideoForm';
import BatchVideoUploadForm from '../forms/BatchVideoUploadForm';

const VideoSwitch = () => {
    const [isBatchUpload, setIsBatchUpload] = useState(false);
// eslint-disable-next-line
    const handleToggle = () => {
        setIsBatchUpload(!isBatchUpload);
    };

    return (
        <div className="app-container">
            <div className="toggle-buttons">
                <button onClick={() => setIsBatchUpload(false)} className={!isBatchUpload ? 'active' : ''}>
                    Single Upload
                </button>
                <button onClick={() => setIsBatchUpload(true)} className={isBatchUpload ? 'active' : ''}>
                    Batch Upload
                </button>
            </div>
            <div className="form-container">
                {isBatchUpload ? <BatchVideoUploadForm /> : <UploadVideoForm />}
            </div>
        </div>
    );
};

export default VideoSwitch;
