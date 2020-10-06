import React, { useState } from 'react'
import { Divider, Table, TableBody, TableCell, TableHead, TablePagination, TableRow } from '@material-ui/core'
import { Attendance, StudentData } from 'services'
import { AttendanceIcon } from '../ui/attendance/AttendanceIcon'

interface AttendanceTableProps {
  students: StudentData[]
}

export const AttendanceTable = ({ students }: AttendanceTableProps) => {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

  const handleChangePage = (event: unknown, newPage: number) => setPage(newPage)

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const studentsInPage = students.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)

  return (
    <>
      <Divider />
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>
              Name
            </TableCell>
            <TableCell align='center' valign='middle'>
              3.10
            </TableCell>
            <TableCell align='center' valign='middle'>
              4.10
            </TableCell>
            <TableCell align='center' valign='middle'>
              5.10
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {studentsInPage.map(s => (
            <TableRow key={s.id}>
              <TableCell>
                {s.name}
              </TableCell>
              <TableCell padding='checkbox' align='center' valign='middle'>
                <AttendanceIcon attendance={Attendance.Attended} />
              </TableCell>
              <TableCell padding='checkbox' align='center' valign='middle'>
                <AttendanceIcon attendance={Attendance.Partial} />
              </TableCell>
              <TableCell padding='checkbox' align='center' valign='middle'>
                <AttendanceIcon attendance={Attendance.Absent} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <TablePagination
        rowsPerPageOptions={[10, 15, 30]}
        component='div'
        count={students.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onChangePage={handleChangePage}
        onChangeRowsPerPage={handleChangeRowsPerPage}
      />
    </>
  )
}
