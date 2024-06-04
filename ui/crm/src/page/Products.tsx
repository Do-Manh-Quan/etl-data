import { Button, Carousel, Drawer, Form, Input, Modal, Select, Space, Table, Tag, message } from 'antd'
import React, { useEffect, useState } from 'react'
import { deleteRequest, getRequest, postRequest } from '../hook/api';
import { useNavigate } from 'react-router-dom';

const Product = () => {
    const [data, setData] = useState<any>([])
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [reload, setReload] = useState(true)
    const [dataDetail, setDataDetail] = useState();
    const navigate = useNavigate()
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
            title: 'title',
            dataIndex: 'title',
            key: 'title',
        },
        {
            title: 'Image',
            dataIndex: 'images',
            key: 'images',
            render: (text) => (
                <Carousel className='w-48' autoplay>
                    {
                        text?.length > 0 && text.map((src, index) => <div className='w-48' key={index}>
                            <img key={index} src={src} />
                        </div>)
                    }
                </Carousel>
            ),
        },
        {
            title: 'price',
            dataIndex: 'price',
            key: 'price',
            render: (text) => (
                <Tag color='geekblue'>{text}</Tag>
            ),
        },
        {
            title: 'url',
            dataIndex: 'url',
            key: 'url',
            render: (text) => <a target='_blank' className='break-all'> {text}</a>
        },
        {
            title: 'Action',
            key: 'action',
            render: (_, record) => (
                <Space size="middle">
                    <Button type='primary' onClick={() => {
                        navigate(record._id)
                    }}>Detail</Button>
                    <Button type='primary' danger onClick={() => {
                        deleteRequest('/product/' + record._id)
                            .then(() => setReload(prev => !prev))
                    }}>Delete</Button>
                </Space>
            ),
        },
    ];
    useEffect(() => {
        getRequest('/product')
            .then(data => {
                let dt_: any = []
                data.map(dt => {
                    if (Array.isArray(dt?.images)) {
                        dt_.push(dt)
                    }
                })
                setData(dt_)

            })
    }, [reload])
    const onFinish = (values) => {
        postRequest('/product', values)
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
            <Table columns={columns} dataSource={data} />
            <Modal title="Create Product" open={isModalOpen} onOk={handleOk} onCancel={handleCancel} footer={null}>
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

export default Product