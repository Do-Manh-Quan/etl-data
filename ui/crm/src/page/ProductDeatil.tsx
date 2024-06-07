import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getRequest } from '../hook/api'
import { Carousel, Rate, Tag } from 'antd'

const ProductDeatil = () => {
    const { id } = useParams()
    const [data, setData] = useState<any>()
    useEffect(() => {
        getRequest(`/product/${id}`)
            .then(data => setData(data))
    }, [])
    return (
        <div className='p-10 flex flex-col gap-10 ob'>
            <div className='grid grid-cols-2 gap-5 h-[80vh]'>
                <div className='h-full'>
                    <Carousel className='w-full h-full' autoplay arrows>
                        {
                            data?.images?.length > 0 && data?.images.map((src, index) => <div className='w-full h-full' key={index}>
                                <img key={index} src={src} className='w-full h-[80vh] object-cover ' />
                            </div>)
                        }
                    </Carousel>
                </div>
                <div className='flex flex-col gap-4 h-full overflow-auto'>
                    <p className='font-bold text-xl'>{data?.title}</p>
                    <p className='font-bold text-xl text-red-600'>{data?.price}</p>
                    {
                        data?.sku?.map(dt => (
                            <div className='flex flex-col gap-3'>
                                <p className='font-bold'>{dt?.type}</p>
                                <div className='flex gap-3 flex-wrap'>
                                    {
                                        dt?.item?.map(d => (<Tag color='blue-inverse'>{d?.label}</Tag>))
                                    }
                                </div>
                            </div>
                        ))
                    }
                    {
                        data?.reviews.length > 0 &&
                        <div className='overflow-auto border border-gray-500 p-4 rounded-lg'>
                            <div className=' flex flex-col gap-4'>
                                {
                                    data?.reviews?.map(dt => (
                                        <div className='flex flex-col'>
                                            <Rate allowHalf value={dt?.start} />
                                            <div>
                                                <Tag>{dt?.sku}</Tag>
                                            </div>
                                            <p>{dt?.review}</p>
                                        </div>
                                    ))
                                }
                            </div>
                        </div>

                    }
                </div>
            </div>
            <p className='font-bold text-xl'>Des</p>
            <div dangerouslySetInnerHTML={{ __html: data?.des }}></div>
        </div>
    )
}

export default ProductDeatil