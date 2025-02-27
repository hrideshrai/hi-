import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, timedelta
from plyer import notification 
import threading

def inaugurate_db():
    conn= sqlite3.connect("medication.db")
    cursor=conn.cursor()
    cursor.execute('''
     CREATE TABLE IF NOT EXISTS medication(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     medicine_name TEXT,
     dosage TEXT,
     regularity TEXT,
     days TEXT,
     times TEXT,
     status TEXT DEFAULT 'Pending')


''')
    
    conn.commit()
    conn.close()

inaugurate_db()

def get_medication():
    conn=sqlite3.connect("medication.db")
    cursor= conn.cursor()
    cursor.execute("SELECT * FROM medication")
    data=cursor.fetchall()
    conn.close()
    return data

def time_format(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
    except ValueError:
        return time_str
    
def days_visibility(event):
    if regularity_var.get()=='Selective days':
        day_frame.pack()

    else:
        day_frame.pack_forget()

def dosage_timing_update(event):
    selected_dosage= int(dosage_var.get()[0])
    for i in range(3):
        if i<selected_dosage:
            time_labels[i].pack()
            time_vars[i].pack()

        else:
            time_labels[i].pack_forget()
            time_vars[i].pack_forget()

            

def add_medication():
    if len (get_medication())>=5:
        messagebox.showerror("Issue","You can add only 5 medicines.")
        return
    
    medicine_name= medicine_name_entry.get()
    dosage=dosage_var.get()
    regularity=regularity_var.get()
    days=",". join([day for day, var in days_vars.items()if var.get()]) if regularity=="Selective days" else""
    selected_dosage= int(dosage[0])
    times= ",".join([time_vars[i].get()for i in range(selected_dosage)])

    if not (medicine_name and dosage and regularity and times):
        messagebox.showerror("Issue", "Kindly all feild must be included!")
        return
    
    conn=sqlite3.connect("medication.db")
    cursor=conn.cursor()
    cursor.execute ("INSERT INTO medication (medicine_name, dosage, regularity, days, times) VALUES(?,?,?,?,?)",(medicine_name, dosage,regularity,days,times))

    conn.commit()
    conn.close()

    messagebox.showinfo("Nice","Successfully medicine updated!!")
    add_window.destroy()
    refresh_display()

def remove_medication(med_id):
    conn=sqlite3.connect("medication.db")
    cursor=conn.cursor()
    cursor.execute("DELETE FROM medication WHERE id=?",(med_id,))
    conn.commit()
    conn.close()
    refresh_display()


def edit_medicine(med_id):
    conn=sqlite3.connect("medication.db")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM medication  WHERE id=?",(med_id,))
    med=cursor.fetchone()
    conn.close()
    open_edit_window(med)


def open_edit_window(med):
    global edit_window, edit_medicine_name_entry, dosage_var, edit_regularity_var, edit_days_vars, edit_time_vars, edit_time_labels, edit_day_frame

    edit_window=tk.Toplevel(root)
    edit_window.title("Edit Medication")
    edit_window.geometry("500x600")

    med_id, medicine_name, dosage, regularity,days, times, status= med
    tk.Label(edit_window, text="Medication Name:").pack()
    edit_regularity_var= ttk.Combobox(edit_window, values=["Daily", "Selective days"])
    edit_regularity_var.set(regularity)
    edit_regularity_var.pack()
    edit_regularity_var.bind("<<ComboboxSelected>>", days_visibility)

    edit_days_vars={}
    edit_day_frame= tk.Frame(edit_window)
    for day in["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
        edit_days_vars[day]=tk.IntVar()
        if days and day in days.split(","):
            edit_days_vars[day].tk.Intvar()
            tk.Checkbutton (edit_day_frame, text=day, variable=edit_days_vars[day]).pack(side=tk.LEFT)

    if regularity=="Selective days":
        edit_day_frame.pack()

        tk.Label(edit_window, text="Dosage:").pack()
        edit_dosage_var=ttk.Combobox(edit_window, values=["1 dose","2 dose","3 dose"])
        edit_dosage_var.set(dosage)
        edit_dosage_var.pack()
        edit_dosage_var.bind("<<CombobocSelected>>", dosage_timing_update)

        edit_time_vars=[]
        edit_time_labels=[]
        times_list=times.split(",")
        for i in range(3):
            edit_time_labels.append(tk.Label(edit_window, text=f"Dosage{i+1}Time:"))
            edit_time_vars.append(ttk.Combobox(edit_window, values=[f"{h:02d}:{m:02d}" for h in range(25) for m in range(0,65, 20)]))
            if i<len(times_list):
                edit_time_vars[i].set(times_list[i])
            edit_time_labels[i].pack()
            edit_time_vars[i].pack()

            tk.Button(edit_window, text="Ok", command=lambda:save_edited_medicine(med_id), bg="#008000", fg="#FFFFFF").pack(pady=11)
            tk.Button(edit_window, text="Quit", command=edit_window.destroy, bg="#FF0000", fg="FFFFFF") .pack()


def save_edited_medicine(med_id):
    medicine_name=edit_medicine_name_entry.get()
    dosage= edit_dosage_var.get()
    regularity=edit_regularity_var.get()
    days=",".join([day for day, var in edit_days_vars.items()if var.get()]) if regularity=="Selective days" else""
    selected_dosage=int(dosage[0])
    times=",".join([edit_time_vars[i].get() for i in range(selected_dosage)]) 
    if not(medicine_name and dosage and regularity and times):
        messagebox.showerror("Issue","All details must be included! ")
        return
    conn=sqlite3.connect("medication.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE medication SET medicine_name=?, dosage=?, regularity=?,days=?,times=? WHERE id=?", (medicine_name, dosage,regularity,days, times, med_id))
    conn.commit()
    conn.close()

    messagebox.showinfo("Great!",":Updated successfullu!!")
    edit_window.destroy()
    refresh_display()

root=tk.Tk()
time_vars={i:tk.StringVar() for i in range(3)}
def refresh_display():
    for widget in display_frame.winfo_children():
        widget.destroy()

    today=datetime.today().strftime('%A,%B,%d,%Y')
    tk.Label(display_frame, text=today,font=("Times New Roman",14,'bold'), bg="#f0f0f0").pack(pady=11)
    medicines= get_medication()
    if medicines:
        for med in medicines:
            med_id, medicine_name,dosage,regularity,days,times, status=med
            tk.Label(display_frame, text=f"Medication:{medicine_name}", font=("Times New Roman", 12,'bold'),bg="#f0f0f0").pack()
            tk.Label(display_frame, text=f"Dosage:{dosage}", font=("Times New Roman",11), bg="#f0f0f0").pack()
            
            times_list=times.split(",")
            for i, time in enumerate(times_list):
                formatted_time=time_format(time.strip())
                tk.Label(display_frame, text=f"{i+1}st Dosage:{formatted_time}",font=("Times New Roman",11),bg="#f0f0f0").pack()

                button_frame=tk.Frame(display_frame, bg="#f0f0f0")
                button_frame.pack()
                tk.Button(button_frame, text="Remove", command= lambda med_id=med_id:remove_medication(med_id),bg="#FF0000", fg="#FFFFFF").pack(side=tk.LEFT, padx=6)
                tk.Button(button_frame, text="Edit", command=lambda med_id=med_id:edit_medicine(med_id),bg="#0000FF", fg="#FFFFFF").pack(side=tk.LEFT, padx=6)
                tk.Label(display_frame, text="---------------------------",bg="#f0f0f0").pack()
            else:
                tk.Label(display_frame, text="Medicines Not Added!!", font=("Times New Roman",11,"bold"), bg="#f0f0f0").pack()
edit_dosage_var=tk.StringVar()
edit_regularity_var=tk.StringVar()
def open_add_window():
    global add_window, medicine_name_entry, dosage_var, regularity_var, days_vars, times_vars, time_labels, day_frame

    add_window=tk.Toplevel(root)
    add_window.title("Add Medication")
    add_window.geometry("500x600")

    tk.Label(add_window, text="Medication Name:").pack()
    medicine_name_entry=tk.Entry(add_window)
    medicine_name_entry.pack()

    tk.Label(add_window, text="Regularity:").pack()
    regularity_var=ttk.Combobox(add_window, values=["Daily","Selective days"])
    regularity_var.pack()
    regularity_var.bind("<<ComboboxSelected>>", days_visibility)

    days_vars={}
    day_frame=tk.Frame(add_window)
    for day in["Monday", "Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
        days_vars[day]=tk.IntVar()
        dosage_var=ttk.Combobox(add_window, values=["1 dose","2 dose","3 dose"])
        dosage_var.pack()
        dosage_var.bind("<<ComboboxSelected>>", dosage_timing_update)

        time_vars=[]

        time_labels=[]
        for i in range(3):
            time_labels.append(tk.Label(add_window, text=f"Dosage{i+1}Time:"))
            time_vars.append(ttk.Combobox(add_window, values=[f"{h:02d}:{m:02d}" for h in range(25) for m in range(0,65,20)]))
        tk.Button(add_window, text= "Next", command=add_medication, bg="#008000", fg="#FFFFFF").pack(pady=11)
        tk.Button(add_window, text="Quit", command=add_window.destroy, bg=" #FF0000", fg="#FFFFFF").pack() 


def check_reminder():
 medicines=get_medication() 
 now=datetime.now().strftime("%H:%M")
 for med in medicines:     
    times_list=med[5].split(",")
    for time in times_list:
 
        if time.strip()==now:
           notification.notify(
             title="Medicine Reminder",
             message=f"Time for taking medication{med[1]}({med[2]})",
            timeout=11

 )

threading.Timer(60, check_reminder).start()

root.title("Medicine_Reminmder")
root.geometry("600x700")
root.configure(bg="#f0f0f0")
tk.Label(root, text="Medicine_Reminder", font=("Arial",15,"bold"), bg="#f0f0f0").pack(pady=11)

display_frame= tk.Frame(root, bg="#f0f0f0", padx=11,pady=11)

display_frame.pack(pady=22)

refresh_display()
tk.Button(root, text="Refresh", command=refresh_display, bg="#0000FF", fg="#FFFFFF").pack(pady=10)
tk.Button(root, text="Add Medication", command=open_add_window, bg="#00008B",fg="#FFFFFF").pack(pady=6)
threading.Thread(target=check_reminder, daemon=True).start()
root.mainloop()
              

















     
      
