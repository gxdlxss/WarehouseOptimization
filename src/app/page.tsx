"use client"

import type * as React from "react"
import {useEffect, useLayoutEffect, useRef, useState} from "react"
import {Button} from "@/components/ui/button"
import {Card, CardContent} from "@/components/ui/card"
import {Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious} from "@/components/ui/carousel"
import {RequestSlide} from "./RequestSlide"
import FileUpload from "@/app/FileLoader"

type Coordinate = [number, number]
export type Request = {
  cells: Coordinate[]
  selection: { request: Record<number, number> }
}

export default function Home() {
  const [warehouse, setWarehouse] = useState<boolean[][]>([])
  const [coordinates, setCoordinates] = useState<Coordinate[]>([])
  const [requests, setRequests] = useState<Request[]>([])
  const socket = useRef<WebSocket | null>(null)

  useLayoutEffect(() => {
    const ws = new WebSocket("ws://192.168.0.100:8765")
    ws.onopen = () => {
      console.log("Connected to server")
      socket.current = ws
    }
    ws.onmessage = (event: MessageEvent) => {
      console.log(JSON.parse(event.data))
    }
  }, [])

  const generateRequest = () => {
    console.log("sended")
    socket.current?.send(
      JSON.stringify({
        type: "get_status",
        requests_count: 64,
      }),
    )
    if (socket.current) {
      socket.current.onmessage = (event: MessageEvent) => {
        const data = JSON.parse(event.data)
        console.log(data)
        if (data.type == "selections") {
          const requests: Request[] = data.body
          setRequests(requests)
        }
      }
    }
  }

  const visualize = () => {
    const additionalCoordinates: Coordinate[] = []
    requests.forEach((request: Request) => {
      additionalCoordinates.push(...request.cells)
    })
    setCoordinates((prevState) => {
      return [...prevState, ...additionalCoordinates]
    })
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8">
      <Card className="w-full max-w-4xl">
        <CardContent className="p-6">
          <FileUpload setWarehouse={setWarehouse} socket={socket}/>
          <Card className="mt-4">
            <CardContent className="p-4">
              <CardContent className='overflow-auto pl-0'>
                {warehouse.length > 0 ? (
                  <div
                    className="grid"
                    style={{
                      gridTemplateColumns: `repeat(${warehouse[0].length}, minmax(0.25rem, 1fr))`,
                      gap: "1px 2px"
                    }}
                  >
                    {warehouse.flatMap((row, i) =>
                      row.map((cell, j) =>
                        <div
                          key={`${i}-${j}`}
                          className={`aspect-square ${
                            coordinates.some(([x, y]) => x === i && y === j)
                              ? "bg-red-500"
                              : cell
                                ? "bg-blue-500"
                                : "bg-gray-200"
                          }`}
                          style={{
                            width: "3px",
                            height: "5px"
                          }}
                        />
                      )
                    )}
                  </div>
                ) : (
                  <p>Загрузите файл для отображения схемы</p>
                )}
              </CardContent>
            </CardContent>
          </Card>
          {warehouse.length > 0 && (
            <CardContent className="p-0 flex flex-col items-center justify-center">
              <CardContent className='flex flex-row pb-0'>
                <Button onClick={generateRequest} className="m-4">
                  Сгенерировать запрос
                </Button>
                <Button onClick={visualize} className="m-4">
                  Визуализировать
                </Button>
              </CardContent>
              {requests.length > 0 && (
                <Carousel className="w-full max-w-xl">
                  <CarouselContent>
                    {requests.map((request: Request, index: number) => (
                      <CarouselItem key={index}>
                        <RequestSlide request={request} index={index}/>
                      </CarouselItem>
                    ))}
                  </CarouselContent>
                  <CarouselPrevious/>
                  <CarouselNext/>
                </Carousel>
              )}
            </CardContent>
          )}
        </CardContent>
      </Card>
    </main>
  )
}

