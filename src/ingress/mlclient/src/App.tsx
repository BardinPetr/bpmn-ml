import React, {useEffect, useState} from 'react';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Alert,
    Button,
    CircularProgress,
    Container,
    LinearProgress,
    Paper,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    FormControlLabel,
    Checkbox,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const API_BASE = 'http://localhost:8000';

interface SubmitRs {
    request_id: string;
    status: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILURE';
    total_tasks: number;
}

interface TaskResult {
    task_id: string;
    status: string;
    result?: any;
    output_file_ids: string[];
    output_image_ids: string[];
    error?: string;
    spent_ms?: number;
}

interface StatusRs {
    request_id: string;
    status: string;
    done_tasks: number;
    total_tasks: number;
    completed_at?: string;
    tasks: TaskResult[];
}

const App: React.FC = () => {
    const [files, setFiles] = useState<File[]>([]);
    const [requestId, setRequestId] = useState<string | null>(null);
    const [status, setStatus] = useState<StatusRs | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [language, setLanguage] = useState<string>('en');
    const [visualize, setVisualize] = useState<boolean>(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) setFiles(Array.from(e.target.files));
    };

    const submit = async () => {
        const formData = new FormData();
        files.forEach(f => formData.append('files', f));
        const parameters = JSON.stringify({ language, visualize });
        formData.append('parameters', parameters);
        try {
            const res = await fetch(`${API_BASE}/submit/d2t`, {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) throw new Error('Submit failed');
            const data: SubmitRs = await res.json();
            setRequestId(data.request_id);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
    };

    useEffect(() => {
        if (!requestId) return;
        const poll = async () => {
            try {
                const res = await fetch(`${API_BASE}/status/${requestId}`);
                if (res.status == 404) return;
                if (!res.ok) throw new Error('Status fetch failed');
                const data: StatusRs = await res.json();
                setStatus(data);
                if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
                    clearInterval(intervalId);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error');
                clearInterval(intervalId);
            }
        };
        poll(); // initial fetch
        const intervalId = setInterval(poll, 500);
        return () => clearInterval(intervalId);
    }, [requestId]);

    const getImageSrc = (fileId: string) => `${API_BASE}/result/${requestId}/${fileId}`;

    const download = (fileId: string) => {
        const a = document.createElement('a');
        a.href = getImageSrc(fileId);
        a.download = fileId;
        a.click();
    };

    return (
        <Container maxWidth="md" sx={{my: 4}}>
            <Typography variant="h4" gutterBottom>ML Image Analyzer</Typography>
            <Paper sx={{p: 2, mb: 2}}>
                <input type="file" multiple accept="image/*" onChange={handleFileChange}/>
                <FormControl sx={{minWidth: 120, ml: 2}}>
                    <InputLabel>Language</InputLabel>
                    <Select value={language} label="Language" onChange={(e) => setLanguage(e.target.value)}>
                        <MenuItem value="en">en</MenuItem>
                        <MenuItem value="ru">ru</MenuItem>
                    </Select>
                </FormControl>
                <FormControlLabel
                    control={<Checkbox checked={visualize} onChange={(e) => setVisualize(e.target.checked)} />}
                    label="Explain/Visualize"
                    sx={{ml: 2}}
                />
                <Button variant="contained" onClick={submit} disabled={files.length === 0} sx={{ml: 2}}>Upload</Button>
                {error && <Alert severity="error">{error}</Alert>}
            </Paper>
            {requestId && status && (
                <Paper sx={{p: 2, mb: 2}}>
                    <Typography>Request: {requestId}</Typography>
                    <Typography>Status: {status.status}</Typography>
                    <Typography>{status.done_tasks} / {status.total_tasks} tasks done</Typography>
                    <LinearProgress variant="determinate" value={(status.done_tasks / status.total_tasks) * 100}/>
                    {status.status === 'PROCESSING' && <CircularProgress/>}
                </Paper>
            )}
            {status?.status === 'SUCCESS' && (
                status.tasks.map((task, idx) => (
                    <Accordion key={task.task_id}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
                            <Typography>Task {idx + 1} ({task.status})</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {task.error && <Alert severity="error">{task.error}</Alert>}
                            {task.result && <pre>{JSON.stringify(task.result, null, 2)}</pre>}
                            {task.output_image_ids.map(id => (
                                <img key={id} src={getImageSrc(id)} alt={id} style={{maxWidth: 300, display: 'block'}}/>
                            ))}
                            {task.output_file_ids.map(id => (
                                <Button key={id} onClick={() => download(id)}>Download {id}</Button>
                            ))}
                        </AccordionDetails>
                    </Accordion>
                ))
            )}
        </Container>
    );
};

export default App;