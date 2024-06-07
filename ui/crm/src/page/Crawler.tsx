import { Button, Drawer, Form, Input, Modal, Select, Space, Table, Tag, message } from 'antd'
import React, { useEffect, useState } from 'react'
import { deleteRequest, getRequest, postRequest } from '../hook/api';

const Crawler = () => {
    const [data, setData] = useState<any>([])
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [reload, setReload] = useState(true)

    const showModal = () => {
        setIsModalOpen(true);
    };

    const handleOk = () => {
        setIsModalOpen(false);
    };

    const handleCancel = () => {
        setIsModalOpen(false);
    };

    const columns: any = [
        {
            title: 'Url',
            dataIndex: 'url',
            key: 'url',
            width: "50%",
            render: (text) => <a className='break-all'>{text}</a>,
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (text) => (
                <Tag color='geekblue'>{text}</Tag>
            ),
        },
        {
            title: 'Type',
            dataIndex: 'type',
            key: 'type',
            render: (text) => (
                <Tag color='geekblue'>{text}</Tag>
            ),
        },
        {
            title: 'Create At',
            dataIndex: 'created_at',
            key: 'created_at',
        },
        {
            title: 'Action',
            key: 'action',
            render: (_, record) => (
                <Space size="middle">
                    {/* <Button type='primary' onClick={() => {

                    }}>Start</Button> */}
                    <Button type='primary' danger onClick={() => {
                        deleteRequest('/crawler/' + record._id)
                            .then(() => setReload(prev => !prev))
                    }}>Delete</Button>
                </Space>
            ),
        },
    ];
    useEffect(() => {
        getRequest('/crawler')
            .then(data => setData(data))
    }, [reload])
    const onFinish = (values) => {
        postRequest('/crawler', values)
            .then(data => {
                setReload(prev => !prev)
                setIsModalOpen(false)
            })
            .catch(err => console.log(err))
    };

    const onFinishFailed = () => {
        message.error("Cần điền đủ các trường")
    };
    return (
        <div className='flex flex-col gap-5 p-5'>
            <div className='flex gap-3'>
                <Button type="primary" onClick={showModal}>
                    Create
                </Button>
                <Button onClick={() => {
                    getRequest('/crawler/start')
                        .then(() => {
                            message.success("Start")
                            setReload(prev => !prev)
                        })
                }}>Start</Button>
            </div>
            <Table columns={columns} dataSource={data} />
            <Modal title="Create Crawler" open={isModalOpen} onOk={handleOk} onCancel={handleCancel} footer={null}>
                <Form
                    layout="vertical"
                    name="basic"
                    onFinish={onFinish}
                    onFinishFailed={onFinishFailed}
                    autoComplete="off"
                >
                    <Form.Item
                        label="Url"
                        name="url"
                        rules={[
                            {
                                required: true,
                                message: 'Hãy nhập Url',
                            },
                        ]}
                    >
                        <Input />
                    </Form.Item>
                    <Form.Item
                        label="Type"
                        name="type"
                        rules={[
                            {
                                required: true,
                                message: 'Hãy nhập type',
                            },
                        ]}
                    >
                        <Select options={[
                            {
                                label: 'Google',
                                value: 'google'
                            },
                            {
                                label: 'Aliexpress',
                                value: 'aliexpress'
                            }
                        ]} />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit" className='w-full'>
                            Xác nhận
                        </Button>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    )
}

export default Crawler