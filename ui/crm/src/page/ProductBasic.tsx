import React, { useEffect, useState } from 'react'
import { getRequest } from '../hook/api'
import { Carousel, Input } from 'antd'
import { useNavigate } from 'react-router-dom'

const ProductBasic = () => {
    const [data, setData] = useState<any>([])
    const [keyword, setKeyword] = useState<any>('')
    useEffect(() => {
        getRequest('/product/search/?title=' + keyword)
            .then(dataProduct => {
                let dt_: any = []
                dataProduct?.products.map(dt => {
                    if (Array.isArray(dt?.images)) {
                        dt_.push(dt)
                    }
                })
                setData(dt_)

            })
    }, [keyword])
    const navigate = useNavigate()
    return (
        <div className='p-4 flex flex-col gap-5'>
            <div className=''>
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder='Search title' />
            </div>
            <div className='grid grid-cols-4 gap-3'>
                {
                    data.length > 0 ? data.map(d => (<div className='bg-white rounded-lg shadow-lg p-4 cursor-pointer' onClick={() => {
                        navigate(`/products/${d?._id}`)
                    }}>
                        <Carousel className='w-full aspect-square' autoplay>
                            {
                                d?.images?.length > 0 && d?.images?.map((src, index) => <div className='w-full h-full' key={index}>
                                    <img key={index} src={src} className='w-full h-full'/>
                                </div>)
                            }
                        </Carousel>
                        <p className='break-all line-clamp-2 font-bold'>{d?.title}</p>
                        <p className='font-bold text-red-500'>{d?.price}</p>
                    </div>))
                        : <div>Not Product</div>
                }
            </div>
        </div>
    )
}

export default ProductBasic