export interface StudentData {
  id: number
  classId: number

  name?: string
  phone?: number
  idNumber?: string
}

export enum Attendance {
  Absent = 0,
  Partial = 1,
  Attended = 2
}

export interface Classroom {
  name: string
  id: number
  students: StudentData[]
}
