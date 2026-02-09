
import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import DashboardLayout from '../components/layout/DashboardLayout';
import WarRoom from '../components/portals/WarRoom';
import JudgeBench from '../components/portals/JudgeBench';

const Dashboard = () => {
    const { role } = useParams();

    // Validate Role
    if (!['accuser', 'accused', 'judge'].includes(role)) {
        return <Navigate to="/" replace />;
    }

    return (
        <DashboardLayout role={role}>
            {role === 'judge' ? <JudgeBench /> : <WarRoom role={role} />}
        </DashboardLayout>
    );
};

export default Dashboard;
