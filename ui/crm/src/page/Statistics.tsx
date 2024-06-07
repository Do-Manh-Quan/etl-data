import React, { useState, useEffect } from 'react'
import { Pie } from '@ant-design/plots';
import { getRequest } from '../hook/api';


const Statistics = () => {
    const [data, setData] = useState([])
    useEffect(() => {
        getRequest('/product/statistics/url')
            .then(dt => setData(dt?.statistics.map(d => ({
                type: d?.root,
                value: d?.count
            }))))
    }, [])
    const config = {
        data,
        angleField: 'value',
        colorField: 'type',
        radius: 0.8,
        label: {
            text: (d) => `${d.type} ${d.value}`,
            position: 'spider',
        },
        legend: {
            color: {
                title: false,
                position: 'right',
                rowPadding: 5,
            },
        },
    };
    return (
        <div className='bg-white h-[90vh]'><Pie {...config}/></div>
    )
}

export default Statistics